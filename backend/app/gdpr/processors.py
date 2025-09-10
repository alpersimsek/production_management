"""
GDPR Tool Processors - Data Processing and Masking

This module provides data processing capabilities for GDPR compliance, handling
both text and binary data formats with comprehensive masking and pattern detection.

Key Components:
- BaseProcessor: Abstract base class for all processor implementations
- TextProcessor: Text file processing with line-by-line masking
- PcapProcessor: Network packet capture file processing with layer-specific masking

Processor Features:
- Multi-Format Support: Handles text files and PCAP network capture files
- Pattern Detection: Uses matchers to identify sensitive data patterns
- Overlap Handling: Intelligent handling of overlapping matches
- Chunk Processing: Efficient processing of large files in chunks
- Error Recovery: Graceful handling of processing errors
- Progress Tracking: Detailed logging of processing progress

TextProcessor Features:
- Line-by-Line Processing: Processes text files line by line for efficiency
- Chunk-Based Processing: Handles large files in manageable chunks
- Pattern Matching: Applies all configured matchers to each line
- Overlap Resolution: Resolves overlapping matches intelligently
- Streaming Output: Yields processed data as it's generated

PcapProcessor Features:
- Network Packet Processing: Processes PCAP files using Scapy library
- Layer-Specific Masking: Masks data at different network layers
- MAC Address Masking: Masks Ethernet layer MAC addresses
- IP Address Masking: Masks IP layer source and destination addresses
- Payload Masking: Masks application layer payload data
- Checksum Recalculation: Recalculates network checksums after modification
- Error Handling: Skips malformed packets while continuing processing

Network Layer Support:
- Ethernet Layer: MAC address masking with proper formatting
- IP Layer: IPv4 address masking with checksum recalculation
- Transport Layer: TCP/UDP checksum recalculation
- Application Layer: Payload text masking with pattern detection

The processors provide the core data processing capabilities for the GDPR tool,
enabling comprehensive masking of sensitive data across different file formats.
"""

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
        # Prioritize specialized matchers to process before generic matchers
        self.matchers = sorted(
            matchers,
            key=lambda m: 0 if isinstance(m, (IPAddrMatcher, MacAddrMatcher, RegexpMatcher)) else 1
        )

    @staticmethod
    def get_overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
        """Returns overlap length between closed intervals a and b."""
        return max(0, min(a[1], b[1]) - max(a[0], b[0]))

    def analyze(self, data):
        result = []
        for matcher in self.matchers:
            try:
                matches = list(matcher.search_iter(data))
                result.append(matches)
            except Exception as e:
                logger.warning(
                    {
                        "event": "matcher_error",
                        "matcher": matcher.__class__.__name__,
                        "error": str(e),
                    },
                    extra={"context": {"matcher": matcher.__class__.__name__}}
                )
                result.append([])

        per_line_matches = []
        for line_matches in zip(*result):
            detected_intervals = []
            filtered_matches = []
            for rule_matches in line_matches:
                for match in rule_matches:
                    try:
                        match_interval = (match.start, match.end)
                        for detected_interval in detected_intervals:
                            if self.get_overlap(match_interval, detected_interval) > 0:
                                break
                        else:
                            detected_intervals.append(match_interval)
                            filtered_matches.append(match)
                    except AttributeError as e:
                        logger.warning(
                            {
                                "event": "invalid_match",
                                "error": str(e),
                                "match_data": str(match),
                                "matcher": rule_matches.__class__.__name__ if rule_matches else "unknown",
                            },
                            extra={"context": {"matcher": rule_matches.__class__.__name__ if rule_matches else "unknown"}}
                        )
                        continue
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
    """PCAP processor class using scapy to mask IP, MAC, and payload data."""
    def feed(self, data: Union[str, pathlib.Path], chunk_size=1000) -> Iterator[Tuple[float, str, int]]:
        from services import PcapProcessingError  # Deferred import
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
                wrpcap(output_path, [])
                yield (0, output_path, DLT_EN10MB)
                return

            linktype = DLT_EN10MB  # Default to Ethernet
            # Log detailed matcher configurations
            matcher_configs = [
                {
                    "type": matcher.__class__.__name__,
                    "pattern": getattr(matcher, 'pattern', None).pattern if hasattr(matcher, 'pattern') else None,
                    "patcher": {
                        "type": matcher.patcher.__class__.__name__,
                        "category": matcher.patcher.category.value if hasattr(matcher.patcher, 'category') else None
                    } if hasattr(matcher, 'patcher') else None
                } for matcher in self.matchers
            ]
            logger.info(
                {
                    "event": "pcap_reader_initialized",
                    "file": str(data),
                    "linktype": linktype,
                    "packet_count": len(packets),
                    "matcher_configs": matcher_configs,
                },
                extra={"context": {"file": str(data)}}
            )
            modified_packets = []
            for pkt in packets:
                try:
                    packet_count += 1
                    
                    # Log progress every 1000 packets
                    if packet_count % 1000 == 0:
                        logger.info({
                            "event": "pcap_progress",
                            "packet_count": packet_count,
                            "total_packets": len(packets),
                            "progress_percent": round((packet_count / len(packets)) * 100, 1)
                        })

                    # Mask Ethernet layer MAC addresses
                    if pkt.haslayer(Ether):
                        ether = pkt[Ether]
                        src_mac = ether.src
                        dst_mac = ether.dst
                        mac_matches = []
                        for matcher in self.matchers:
                            if isinstance(matcher, RegexpMatcher):
                                if matcher.pattern.match(src_mac):
                                    mac_matches.append(Match(
                                        start=0, end=len(src_mac), word=src_mac,
                                        patcher=matcher.patcher
                                    ))
                                if matcher.pattern.match(dst_mac):
                                    mac_matches.append(Match(
                                        start=0, end=len(dst_mac), word=dst_mac,
                                        patcher=matcher.patcher
                                    ))
                        for match in mac_matches:
                            masked_mac = match.process()
                            if match.word == src_mac:
                                ether.src = masked_mac
                                logger.info(
                                    {
                                        "event": "mac_masked",
                                        "packet_count": packet_count,
                                        "field": "src",
                                        "original": src_mac,
                                        "masked": masked_mac,
                                    },
                                    extra={"context": {"packet_count": packet_count}}
                                )
                            elif match.word == dst_mac:
                                ether.dst = masked_mac
                                logger.info(
                                    {
                                        "event": "mac_masked",
                                        "packet_count": packet_count,
                                        "field": "dst",
                                        "original": dst_mac,
                                        "masked": masked_mac,
                                    },
                                    extra={"context": {"packet_count": packet_count}}
                                )

                    # Mask IP layer addresses
                    if pkt.haslayer(IP):
                        ip = pkt[IP]
                        src_ip = ip.src
                        dst_ip = ip.dst
                        ip_matches = []
                        for matcher in self.matchers:
                            if isinstance(matcher, RegexpMatcher):
                                if matcher.pattern.match(src_ip):
                                    ip_matches.append(Match(
                                        start=0, end=len(src_ip), word=src_ip,
                                        patcher=matcher.patcher
                                    ))
                                if matcher.pattern.match(dst_ip):
                                    ip_matches.append(Match(
                                        start=0, end=len(dst_ip), word=dst_ip,
                                        patcher=matcher.patcher
                                    ))
                        for match in ip_matches:
                            masked_ip = match.process()
                            if match.word == src_ip:
                                ip.src = masked_ip
                                logger.info(
                                    {
                                        "event": "ip_masked",
                                        "packet_count": packet_count,
                                        "field": "src",
                                        "original": src_ip,
                                        "masked": masked_ip,
                                    },
                                    extra={"context": {"packet_count": packet_count}}
                                )
                            elif match.word == dst_ip:
                                ip.dst = masked_ip
                                logger.info(
                                    {
                                        "event": "ip_masked",
                                        "packet_count": packet_count,
                                        "field": "dst",
                                        "original": dst_ip,
                                        "masked": masked_ip,
                                    },
                                    extra={"context": {"packet_count": packet_count}}
                                )

                    # Extract and mask payload as text
                    payload = None
                    if pkt.haslayer(Raw):
                        try:
                            payload = pkt[Raw].load.decode('utf-8', errors='ignore')
                        except Exception as ex:
                            logger.warning({
                                "event": "payload_decode_warning",
                                "packet_count": packet_count,
                                "error": f"Cannot decode payload: {str(ex)}",
                            })
                            payload = None

                    if payload:
                        chunk_matches = self.analyze([payload])
                        if chunk_matches[0]:
                            masked_payload = self.process(payload, chunk_matches[0])
                            pkt[Raw].load = masked_payload.encode('utf-8')

                    # Recalculate checksums if modified
                    if pkt.haslayer(IP):
                        pkt[IP].chksum = None
                        if pkt.haslayer(TCP):
                            pkt[TCP].chksum = None
                        elif pkt.haslayer(UDP):
                            pkt[UDP].chksum = None
                        pkt = pkt.__class__(bytes(pkt))

                    modified_packets.append(pkt)
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
                    modified_packets.append(pkt)
                    continue

            wrpcap(output_path, modified_packets, linktype=linktype)
            logger.info(
                {
                    "event": "pcap_processing_summary",
                    "total_packets": packet_count,
                    "skipped_packets": skipped_packets,
                    "success_rate": round(((packet_count - skipped_packets) / packet_count) * 100, 1) if packet_count > 0 else 0,
                    "output_file": output_path,
                },
                extra={"context": {"file": str(data)}}
            )
            yield (0, output_path, linktype)
        except Exception as ex:
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