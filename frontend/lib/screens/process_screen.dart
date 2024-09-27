import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/widgets/app_drawer.dart';
import 'dart:async';

class ProcessScreen extends StatefulWidget {
  final UserModel user;
  String fileName; // The file selected to be processed

  ProcessScreen({super.key, required this.user, required this.fileName});

  @override
  State<ProcessScreen> createState() => _ProcessScreenState();
}

class _ProcessScreenState extends State<ProcessScreen> {
  List<String> uploadedFiles = [];
  List<String> processedFiles = [];
  bool uploadFileExist = false;
  bool processedFileExists = false;
  Dio dio = Dio(); // Initialize Dio
  double processProgress = 0.0; // Track processing progress
  double maskingProgress = 0.0;
  double zipMaskProgress = 0.0;
  Timer? progressTimer; // Timer to poll the progress
  String? taskId; // Track task ID returned by the backend
  String? maskTaskId;
  String? zipMaskTaskId;

  String backendUrl = dotenv.env['API_URL'] ?? 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    _fetchUploadedFiles();
    _fetchProcessedFiles();
  }

  @override
  void dispose() {
    progressTimer?.cancel(); // Clean up the timer
    super.dispose();
  }

  // Fetch uploaded files from the backend
  Future<void> _fetchUploadedFiles() async {
    final response = await dio.get(
      '$backendUrl/files/${widget.user.username}/uploads',
    );
    if (response.statusCode == 200) {
      setState(() {
        uploadedFiles = List<String>.from(response.data['files']);
        uploadFileExist = uploadedFiles.isNotEmpty;
      });
    }
  }

  // Fetch processed files from the backend
  Future<void> _fetchProcessedFiles() async {
    final response = await dio.get(
      '$backendUrl/files/${widget.user.username}/processed',
    );
    if (response.statusCode == 200) {
      setState(() {
        processedFiles = List<String>.from(response.data['files']);
        processedFileExists = processedFiles.isNotEmpty;
      });
    }
  }

  // Start polling the backend for progress updates
  void startPollingProgress(String taskId) {
    progressTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      final progressResponse = await dio.get(
        '$backendUrl/files/process/progress/$taskId',
      );
      final progress = progressResponse.data['progress'];

      setState(() {
        processProgress = progress;
      });

      if (progress >= 100) {
        timer.cancel(); // Stop polling when processing is done
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File processed successfully!")),
        );
        _fetchProcessedFiles();
        _maskFiles(widget.fileName); // Refresh processed files list
      } else if (progress == -1) {
        timer.cancel();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File processing failed!")),
        );
      }
    });
  }

  // Process selected file
  Future<void> _processFile(String filename) async {
    final response = await dio.post(
      '$backendUrl/files/process/$filename',
      data: {"username": widget.user.username},
    );
    if (response.statusCode == 200) {
      setState(() {
        taskId = response.data['task_id']; // Retrieve task ID from backend
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File processing started!")),
      );
      startPollingProgress(taskId!); // Start polling progress
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to start processing!")),
      );
    }
  }

  // Start polling the backend for progress updates
  void startPollingMasking(String taskId) {
    progressTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      final progressResponse = await dio.get(
        '$backendUrl/files/masking/progress/$taskId',
      );
      final progress = progressResponse.data['progress'];
      print(progress);

      setState(() {
        maskingProgress = progress;
      });

      if (progress >= 100) {
        timer.cancel(); // Stop polling when processing is done
        _zipMaskFiles(widget.fileName);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File(s) masked successfully!")),
        );
        // _fetchProcessedFiles();
      } else if (progress == -1) {
        timer.cancel();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File(s) masking failed!")),
        );
      }
    });
  }

  // Process selected file
  Future<void> _maskFiles(String filename) async {
    final response = await dio.post(
      '$backendUrl/files/mask/$filename',
      data: {"username": widget.user.username},
    );
    if (response.statusCode == 200) {
      setState(() {
        maskTaskId = response.data['maskTask_id'];
        print(maskTaskId); // Retrieve task ID from backend
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File masking started!")),
      );
      startPollingMasking(maskTaskId!); // Start polling progress
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to start masking!")),
      );
    }
  }

  // Start polling the backend for progress updates
  void startPollingMaskZip(String taskId) {
    progressTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      final progressResponse = await dio.get(
        '$backendUrl/files/masking/zip/$taskId',
      );
      final progress = progressResponse.data['progress'];

      setState(() {
        zipMaskProgress = progress;
      });

      if (progress >= 100) {
        timer.cancel(); // Stop polling when processing is done
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File(s) Archive successfully!")),
        );
        // _fetchProcessedFiles();
      } else if (progress == -1) {
        timer.cancel();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File(s) Archive failed!")),
        );
      }
    });
  }

  // Process selected file
  Future<void> _zipMaskFiles(String filename) async {
    final response = await dio.post(
      '$backendUrl/files/zipMask/$filename',
      data: {"username": widget.user.username},
    );
    if (response.statusCode == 200) {
      setState(() {
        zipMaskTaskId = response.data['zipMaskTask_id'];
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Mask Files Archive started!")),
      );
      startPollingMaskZip(zipMaskTaskId!); // Start polling progress
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to start Mask Files Archive!")),
      );
    }
  }

  // Delete uploaded file
  Future<void> _deleteUploadFile(String filename) async {
    final response = await dio.delete(
      '$backendUrl/files/delete/${widget.user.username}/uploads/$filename',
    );
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File deleted successfully!")),
      );
      _fetchUploadedFiles(); // Refresh uploaded files
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to delete file!")),
      );
    }
  }

  // Delete processed file
  Future<void> _deleteProcessFile(String filename) async {
    final response = await dio.delete(
      '$backendUrl/files/delete/${widget.user.username}/processed/$filename',
    );
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File deleted successfully!")),
      );
      _fetchProcessedFiles(); // Refresh processed files
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to delete file!")),
      );
    }
  }

  // Download processed file
  Future<void> _downloadFile(String filename) async {
    final response = await dio.get(
      '$backendUrl/files/download/${widget.user.username}/$filename',
      options: Options(responseType: ResponseType.bytes),
    );
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File download triggered!")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to download file!")),
      );
    }
  }

  // Update the selected file name
  void _selectFile(String filename) {
    setState(() {
      widget.fileName = filename;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('GDPR Process'),
      ),
      drawer: AppDrawer(user: widget.user),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 20),
            DataTable(
              columns: const [
                DataColumn(label: Text('Filename')),
                DataColumn(label: Text('Actions')),
              ],
              rows: [
                DataRow(
                  cells: [
                    DataCell(Text(widget.fileName)),
                    DataCell(ElevatedButton(
                      onPressed: () => _processFile(widget.fileName),
                      child: const Text('Process This File'),
                    )),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Display processing progress
            if (processProgress > 0 && processProgress < 100)
              Column(
                children: [
                  LinearProgressIndicator(value: processProgress / 100),
                  const SizedBox(height: 10),
                  Text(
                      'Processing Progress: ${(processProgress).toStringAsFixed(2)}%'),
                ],
              ),
            if (maskingProgress > 0 && maskingProgress < 100)
              Column(
                children: [
                  LinearProgressIndicator(value: maskingProgress / 100),
                  const SizedBox(height: 10),
                  Text(
                      'Masking Progress: ${(maskingProgress).toStringAsFixed(2)}%'),
                ],
              ),
            if (zipMaskProgress > 0 && zipMaskProgress < 100)
              Column(
                children: [
                  LinearProgressIndicator(value: zipMaskProgress / 100),
                  const SizedBox(height: 10),
                  Text(
                      'Masked File(s) Archieve Progress: ${(zipMaskProgress).toStringAsFixed(2)}%'),
                ],
              ),
            // Uploaded files section
            if (uploadFileExist) const Text('Uploaded Files'),
            if (uploadedFiles.isNotEmpty)
              DataTable(
                columns: const [
                  DataColumn(label: Text('Filename')),
                  DataColumn(label: Text('Actions')),
                ],
                rows: uploadedFiles.map((file) {
                  return DataRow(cells: [
                    DataCell(Text(file)),
                    DataCell(Row(
                      children: [
                        ElevatedButton(
                          onPressed: () => _selectFile(file),
                          child: const Text('Select This File'),
                        ),
                        const SizedBox(width: 10),
                        ElevatedButton(
                          onPressed: () => _deleteUploadFile(file),
                          child: const Text('Delete'),
                        ),
                      ],
                    )),
                  ]);
                }).toList(),
              ),

            const SizedBox(height: 20),

            // Processed files section
            if (processedFileExists) const Text('Processed Files'),
            if (processedFiles.isNotEmpty)
              DataTable(
                columns: const [
                  DataColumn(label: Text('Filename')),
                  DataColumn(label: Text('Actions')),
                ],
                rows: processedFiles.map((file) {
                  return DataRow(cells: [
                    DataCell(Text(file)),
                    DataCell(Row(
                      children: [
                        ElevatedButton(
                          onPressed: () => _downloadFile(file),
                          child: const Text('Download'),
                        ),
                        const SizedBox(width: 10),
                        ElevatedButton(
                          onPressed: () => _deleteProcessFile(file),
                          child: const Text('Delete'),
                        ),
                      ],
                    )),
                  ]);
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }
}
