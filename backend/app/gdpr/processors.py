import abc
import itertools
import os
from gdpr.matchers import BaseMatcher, RegexpMatcher, IPAddrMatcher, MacAddrMatcher, Match
from typing import Union, Sequence, Mapping, Any, Optional, Iterator, Tuple
from scapy.all import rdpcap, wrpcap, Packet, DLT_EN10MB
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Raw
import pathlib
from logger import logger

class BaseProcessor(abc.ABC):
    """Base processor class."""
    def __init__(self, matchers: Sequence[BaseMatcher]):
        self.matchers = matchers

    @staticmethod
    def get_overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
        """Returns overlap length between closed intervals a and b."""
        return max(0, min(a[1], b[1]) - max(a[0], b[0]))

    def analyze(self, data):
        result = []
        for matcher in self.matchers:
            matches = list(matcher.search_iter(data))
            result.append(matches)

        per_line_matches = []
        for line_matches in zip(*result):
            detected_intervals = []
            filtered_matches = []
            for rule_matches in line_matches:
                for match in rule_matches:
                    match_interval = (match.start, match.end)
                    for detected_interval in detected_intervals:
                        if self.get_overlap(match_interval, detected_interval) > 0:
                            break
                    else:
                        detected_intervals.append(match_interval)
                        filtered_matches.append(match)
            filtered_matches.sort(key=lambda x: x.start)
            per_line_matches.append(filtered_matches)
        return per_line_matches

    def process(self, data, matches: Sequence[Match]):
        if not matches:
            return data

        patched = []
        first_match_start = matches[0].start
        if first_match_start != 0:
            patched.append(data[:first_match_start])

        last_match_id = len(matches) - 1

        for i, match in enumerate(matches):
            patched.append(match.process())
            if i < last_match_id:
                next_match = matches[i + 1]
                patched.append(data[match.end:next_match.start])
            else:
                patched.append(data[match.end:])

        if isinstance(data, str):
            join_char = ''
        else:
            join_char = b''
        patched = join_char.join(patched)
        return patched

    @abc.abstractmethod
    def feed(self, data, chunk_size=1000):
        raise NotImplementedError()

class TextProcessor(BaseProcessor):
    """Text processor class."""
    def feed(self, data, chunk_size=1000) -> Iterator[bytes]:
        data = iter(data)
        while True:
            chunk = list(itertools.islice(data, chunk_size))
            if not chunk:
                break
            chunk_matches = self.analyze(chunk)
            for line, matches in zip(chunk, chunk_matches):
                line = self.process(line, matches)
                yield line

class PcapProcessor(BaseProcessor):
    """PCAP processor class using scapy to process payloads as text."""
    def feed(self, data: Union[str, pathlib.Path], chunk_size=1000) -> Iterator[Tuple[float, str, int]]:
        from services import PcapProcessingError  # Deferred import to avoid circular dependency
        packet_count = 0
        skipped_packets = 0
        output_path = str(data) + ".tmp"
        try:
            # Read PCAP file using scapy
            packets = rdpcap(str(data))
            if not packets:
                logger.warning(
                    {
                        "event": "empty_pcap",
                        "file": str(data),
                        "message": "No packets found in PCAP file",
                    },
                    extra={"context": {"file": str(data)}}
                )
                # Create an empty PCAP file as output
                wrpcap(output_path, [])
                yield (0, output_path, DLT_EN10MB)
                return

            # Use DLT_EN10MB (Ethernet) as default linktype
            linktype = DLT_EN10MB
            logger.info(
                {
                    "event": "pcap_reader_initialized",
                    "file": str(data),
                    "linktype": linktype,
                    "packet_count": len(packets),
                },
                extra={"context": {"file": str(data)}}
            )
            modified_packets = []
            for pkt in packets:
                try:
                    packet_count += 1
                    # Outline packet layers
                    layers = []
                    current = pkt
                    while current:
                        layers.append(current.name)
                        current = current.payload
                    logger.debug(
                        {
                            "event": "packet_layers",
                            "packet_count": packet_count,
                            "layers": layers,
                            "timestamp": pkt.time,
                        },
                        extra={"context": {"packet_count": packet_count}}
                    )

                    # Extract payload as text
                    payload = None
                    if pkt.haslayer(Raw):
                        try:
                            payload = pkt[Raw].load.decode('utf-8', errors='ignore')
                            logger.debug(
                                {
                                    "event": "payload_extracted",
                                    "packet_count": packet_count,
                                    "payload_length": len(payload),
                                    "payload_preview": payload[:50],  # First 50 chars for debugging
                                },
                                extra={"context": {"packet_count": packet_count}}
                            )
                        except Exception as ex:
                            logger.warning(
                                {
                                    "event": "payload_decode_warning",
                                    "packet_count": packet_count,
                                    "error": f"Cannot decode payload: {str(ex)}",
                                },
                                extra={"context": {"packet_count": packet_count}}
                            )
                            payload = None

                    if payload:
                        # Analyze and process payload as text
                        chunk_matches = self.analyze([payload])
                        if chunk_matches[0]:  # Matches for the single line
                            masked_payload = self.process(payload, chunk_matches[0])
                            # Update packet payload
                            pkt[Raw].load = masked_payload.encode('utf-8')
                            logger.debug(
                                {
                                    "event": "payload_masked",
                                    "packet_count": packet_count,
                                    "original_length": len(payload),
                                    "masked_length": len(masked_payload),
                                },
                                extra={"context": {"packet_count": packet_count}}
                            )

                    # Recalculate checksums if IP layer exists
                    if pkt.haslayer(IP):
                        pkt[IP].chksum = None  # Force recalculation
                        if pkt.haslayer(TCP):
                            pkt[TCP].chksum = None
                        elif pkt.haslayer(UDP):
                            pkt[UDP].chksum = None
                        # Rebuild packet to update checksums
                        pkt = pkt.__class__(bytes(pkt))

                    modified_packets.append(pkt)
                    logger.debug(
                        {
                            "event": "packet_processed",
                            "packet_count": packet_count,
                            "packet_length": len(pkt),
                        },
                        extra={"context": {"packet_count": packet_count}}
                    )
                except Exception as ex:
                    skipped_packets += 1
                    logger.warning(
                        {
                            "event": "packet_processing_warning",
                            "packet_count": packet_count,
                            "error": f"Skipping packet: {str(ex)}",
                        },
                        extra={"context": {"packet_count": packet_count}}
                    )
                    modified_packets.append(pkt)  # Keep original packet
                    continue

            # Save modified packets to a temporary output file
            wrpcap(output_path, modified_packets, linktype=linktype)
            logger.info(
                {
                    "event": "pcap_processing_summary",
                    "total_packets": packet_count,
                    "skipped_packets": skipped_packets,
                    "output_file": output_path,
                },
                extra={"context": {"file": str(data)}}
            )
            # Yield the path to the modified PCAP file
            yield (0, output_path, linktype)
        except Exception as ex:
            # Clean up temporary file on error
            if os.path.exists(output_path):
                os.unlink(output_path)
            logger.error(
                {
                    "event": "pcap_processing_error",
                    "file": str(data),
                    "error": str(ex),
                },
                extra={"context": {"file": str(data)}}
            )
            raise PcapProcessingError(f"Failed to process PCAP file: {str(ex)}")
        finally:
            # Ensure temporary file is cleaned up if not yielded
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception as ex:
                    logger.warning(
                        {
                            "event": "temp_file_cleanup_failed",
                            "file": output_path,
                            "error": str(ex),
                        },
                        extra={"context": {"file": output_path}}
                    )