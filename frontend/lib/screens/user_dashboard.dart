import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_elastic_list_view/flutter_elastic_list_view.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/screens/admin_dashboard.dart';
import 'package:frontend/screens/gdpr_mask_screen.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/user_model.dart';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:frontend/screens/styles/app_colors.dart';
import 'package:frontend/screens/styles/app_styles.dart';
import 'dart:html' as html;

import 'package:frontend/screens/styles/progress_indicator.dart';

class UserDashboard extends StatefulWidget {
  final UserModel user;

  const UserDashboard({super.key, required this.user});

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
  PlatformFile? selectedFile;

  List<String> uploadedFiles = [];
  List<String> processedFiles = [];
  bool uploadFileExist = false;
  bool processedFileExists = false;
  double uploadProgress = 0.0;
  bool isUploading = false;
  Dio dio = Dio();
  double processProgress = 0.0; // Track processing progress
  double maskingProgress = 0.0;
  double zipMaskProgress = 0.0;
  Timer? progressTimer; // Timer to poll the progress
  String? taskId; // Track task ID returned by the backend
  String? maskTaskId;
  String? zipMaskTaskId;
  String? selectedProcFile;

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

  Future<void> pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles();

    if (result != null) {
      setState(() {
        selectedFile = result.files.first;
        uploadProgress = 0.0;
      });
    }
  }

  Future<void> uploadFile() async {
    if (selectedFile != null) {
      setState(() {
        isUploading = true;
      });
      String fileName = selectedFile!.name;

      FormData formData = FormData.fromMap({
        "username": widget.user.username,
        "file":
            MultipartFile.fromBytes(selectedFile!.bytes!, filename: fileName),
      });

      try {
        var response = await dio.post(
          "http://localhost:8000/files/upload",
          data: formData,
          onSendProgress: (int sent, int total) {
            setState(() {
              uploadProgress = sent / total;
            });
          },
        );

        if (response.statusCode == 200) {
          setState(() {
            selectedFile = null;
            uploadProgress = 0.0;
            isUploading = false;
          });
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("File uploaded successfully!")),
          );
          _fetchUploadedFiles();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("File upload failed!")),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: $e")),
        );
      }
    }
  }

  Future<void> _fetchUploadedFiles() async {
    final response = await dio.get(
      'http://localhost:8000/files/${widget.user.username}/uploads',
    );
    if (response.statusCode == 200) {
      setState(() {
        uploadedFiles = List<String>.from(response.data['files']);
        uploadFileExist = uploadedFiles.isNotEmpty;
      });
    }
  }

  Future<void> _fetchProcessedFiles() async {
    final response = await dio.get(
      'http://localhost:8000/files/${widget.user.username}/processed',
    );
    if (response.statusCode == 200) {
      setState(() {
        processedFiles = List<String>.from(response.data['files']);
        processedFileExists = processedFiles.isNotEmpty;
      });
    }
  }

  Future<void> _deleteUploadFile(String filename) async {
    final response = await dio.delete(
      'http://localhost:8000/files/delete/${widget.user.username}/uploads/$filename',
    );
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File deleted successfully!")),
      );
      _fetchUploadedFiles();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to delete file!")),
      );
    }
  }

  Future<void> _deleteProcessFile(String filename) async {
    final response = await dio.delete(
      'http://localhost:8000/files/delete/${widget.user.username}/processed/$filename',
    );
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("File deleted successfully!")),
      );
      _fetchProcessedFiles();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to delete file!")),
      );
    }
  }

  // Start polling the backend for progress updates
  void startPollingProgress(String taskId) {
    progressTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      final progressResponse = await dio.get(
        'http://localhost:8000/files/process/progress/$taskId',
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
        _maskFiles(selectedProcFile!); // Refresh processed files list
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
      'http://localhost:8000/files/process/$filename',
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
        'http://localhost:8000/files/masking/progress/$taskId',
      );
      final progress = progressResponse.data['progress'];
      print(progress);

      setState(() {
        maskingProgress = progress;
      });

      if (progress >= 100) {
        timer.cancel(); // Stop polling when processing is done
        _zipMaskFiles(selectedProcFile!);
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
      'http://localhost:8000/files/mask/$filename',
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
        'http://localhost:8000/files/masking/zip/$taskId',
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
        _fetchProcessedFiles();
      } else if (progress == -1) {
        timer.cancel();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File(s) Archive failed!")),
        );
      }
    });
  }

  Future<void> _downloadFile(String filename) async {
    try {
      // Make the request to download the file
      final response = await dio.get(
        'http://localhost:8000/files/download/${widget.user.username}/$filename',
        options: Options(responseType: ResponseType.bytes),
      );

      if (response.statusCode == 200) {
        // Convert the response data (bytes) into a blob
        final blob = html.Blob([response.data]);

        // Create a link element for downloading
        final url = html.Url.createObjectUrlFromBlob(blob);
        final anchor = html.AnchorElement(href: url)
          ..setAttribute("download", filename)
          ..click();

        // Clean up the URL object
        html.Url.revokeObjectUrl(url);

        // Notify user that the file download is triggered
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("File download triggered!")),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Failed to download file!")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: $e")),
      );
    }
  }

  // Process selected file
  Future<void> _zipMaskFiles(String filename) async {
    final response = await dio.post(
      'http://localhost:8000/files/zipMask/$filename',
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

  BoxDecoration neumorphicDecoration({double borderRadius = 12.0}) {
    return BoxDecoration(
      color: AppColors.backColor,
      borderRadius: BorderRadius.circular(borderRadius),
      boxShadow: [
        BoxShadow(
          color: Colors.grey.shade300,
          offset: const Offset(-5, -5),
          blurRadius: 15,
          spreadRadius: 1,
        ),
        BoxShadow(
          color: Colors.grey.shade800,
          offset: const Offset(5, 5),
          blurRadius: 15,
          spreadRadius: 1,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    // Get the screen dimensions
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    // Determine the crossAxisCount based on screen width (for responsiveness)
    int crossAxisCount = screenWidth > 800 ? 2 : 1;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.grey.shade200,
        title: Text(
          'GDPR Processor',
          style: (montserrat.copyWith(
              fontSize: 36,
              fontWeight: FontWeight.bold,
              color: AppColors.mainBackColor)),
        ),
        leading: IconButton(
          alignment: Alignment.centerRight,
          onPressed: () {},
          icon: Image.asset(
            color: Colors.blueGrey,
            filterQuality: FilterQuality.high,
            'icons/document.png',
          ),
        ),
        actions: [
          if (widget.user.role == 'admin')
            IconButton(
              icon: const Icon(
                Icons.admin_panel_settings_rounded,
                size: 40,
              ),
              onPressed: () {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(
                    builder: (context) => AdminDashboard(
                      userMod: widget.user,
                    ),
                  ),
                );
              },
            ),
          IconButton(
            icon: const Icon(
              Icons.map,
              size: 40,
            ),
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (context) => GdprMapScreen(
                    user: widget.user,
                  ),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(
              Icons.logout_outlined,
              size: 40,
            ),
            onPressed: () {
              context.read<AuthBloc>().add(AuthLogoutEvent());
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (context) => LoginScreen(),
                ),
              );
            },
          ),
        ],
      ),
      backgroundColor: AppColors.greyColor,
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Container(
                  decoration: neumorphicDecoration(borderRadius: 16),
                  child: ElevatedButton(
                    onPressed: pickFile,
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(
                        horizontal: MediaQuery.of(context).size.width * 0.01,
                        vertical: MediaQuery.of(context).size.height * 0.02,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      backgroundColor: AppColors.mainBackColor,
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize
                          .min, // Keep the button tight to the content
                      children: [
                        Image.asset(
                          'icons/add.png', // Image path
                          height: 40,
                          color: Colors.white, // Adjust the height of the image
                        ),
                        const SizedBox(
                            width: 8), // Add space between image and text
                        Text(
                          'Select File',
                          style: (ralewayStyle.copyWith(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: AppColors.whiteColor)),
                        ),
                      ],
                    ),
                  ),
                ),
                if (selectedFile != null)
                  Text(
                    'Selected File: ${selectedFile!.name}',
                    style: (ralewayStyle.copyWith(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textColor)),
                  ),
                if (selectedFile != null)
                  Container(
                    decoration: neumorphicDecoration(borderRadius: 16),
                    child: ElevatedButton(
                      onPressed: uploadFile,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(
                          horizontal: MediaQuery.of(context).size.width * 0.01,
                          vertical: MediaQuery.of(context).size.height * 0.02,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        backgroundColor: AppColors.mainBackColor,
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize
                            .min, // Keep the button tight to the content
                        children: [
                          Image.asset(
                            'icons/submit.png', // Image path
                            height: 40,
                            color:
                                Colors.white, // Adjust the height of the image
                          ),
                          const SizedBox(
                              width: 8), // Add space between image and text
                          Text(
                            'Upload Selected',
                            style: (ralewayStyle.copyWith(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: AppColors.whiteColor)),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
            if (isUploading)
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Uploading...',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(height: 10),
                  GradientProgressIndicator(
                    progress: uploadProgress,
                    color1: Colors.grey,
                    color2: Colors.blue,
                    color3: Colors.green,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Upload Progress: ${(uploadProgress * 100).toStringAsFixed(2)}%',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            // Display processing progress
            if (processProgress > 0 && processProgress < 100)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Processing...',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.orangeAccent,
                    ),
                  ),
                  const SizedBox(height: 10),
                  GradientProgressIndicator(
                    progress: processProgress / 100,
                    color1: Colors.grey,
                    color2: Colors.blue,
                    color3: Colors.green,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Processing Progress: ${(processProgress).toStringAsFixed(2)}%',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            if (maskingProgress > 0 && maskingProgress < 100)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Masking...',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.greenAccent,
                    ),
                  ),
                  const SizedBox(height: 10),
                  GradientProgressIndicator(
                    progress: maskingProgress / 100,
                    color1: Colors.grey,
                    color2: Colors.blue,
                    color3: Colors.green,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Masking Progress: ${(maskingProgress).toStringAsFixed(2)}%',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            if (zipMaskProgress > 0 && zipMaskProgress < 100)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Archiving...',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.purpleAccent,
                    ),
                  ),
                  const SizedBox(height: 10),
                  LinearProgressIndicator(
                    value: zipMaskProgress / 100,
                    minHeight: 8,
                    backgroundColor: Colors.grey[300],
                    valueColor: const AlwaysStoppedAnimation<Color>(
                        Colors.purpleAccent),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Archive Progress: ${(zipMaskProgress).toStringAsFixed(2)}%',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            const SizedBox(
              height: 50,
            ),
            SizedBox(
              height: screenHeight *
                  0.07, // Set the height to half of the screen height
              child: Column(
                children: [
                  if (uploadFileExist)
                    Row(
                      mainAxisAlignment: processedFileExists
                          ? MainAxisAlignment.spaceAround
                          : MainAxisAlignment.center,
                      children: [
                        uploadFileExist
                            ? Text(
                                'Uploaded Files',
                                style: (ralewayStyle.copyWith(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.blueDarkColor)),
                              )
                            : SizedBox.shrink(),
                        processedFileExists
                            ? Text(
                                'Processed Files',
                                style: (ralewayStyle.copyWith(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.blueDarkColor)),
                              )
                            : SizedBox.shrink()
                      ],
                    ),
                ],
              ),
            ),
            Expanded(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  if (uploadFileExist)
                    Flexible(
                      flex: 1,
                      child: Padding(
                        padding: const EdgeInsets.all(10.0),
                        child: ElasticListView.builder(
                          itemCount: uploadedFiles.length,
                          itemBuilder: (context, index) {
                            return Container(
                              height: 75,
                              margin: const EdgeInsets.fromLTRB(5, 5, 20, 5),
                              decoration:
                                  neumorphicDecoration(borderRadius: 16),
                              child: ListTile(
                                contentPadding: const EdgeInsets.all(10),
                                title: Text(
                                  uploadedFiles[index],
                                  style: (ralewayStyle.copyWith(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.blueDarkColor)),
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    Container(
                                      decoration: neumorphicDecoration(
                                          borderRadius: 16),
                                      child: ElevatedButton(
                                        onPressed: () {
                                          setState(() {
                                            selectedProcFile =
                                                uploadedFiles[index];
                                          });
                                          _processFile(selectedProcFile!);
                                        },
                                        style: ElevatedButton.styleFrom(
                                          padding: EdgeInsets.symmetric(
                                            horizontal: MediaQuery.of(context)
                                                    .size
                                                    .width *
                                                0.01,
                                            vertical: MediaQuery.of(context)
                                                    .size
                                                    .height *
                                                0.02,
                                          ),
                                          shape: RoundedRectangleBorder(
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          backgroundColor:
                                              AppColors.mainBackColor,
                                        ),
                                        child: const Text(
                                          'Process',
                                          style: TextStyle(color: Colors.white),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    IconButton(
                                      icon: const Icon(
                                        Icons.delete,
                                        color: Colors.red,
                                        size: 30,
                                      ),
                                      onPressed: () => _deleteUploadFile(
                                          uploadedFiles[index]),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  if (processedFileExists)
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.all(10.0),
                        child: ElasticListView.builder(
                          elasticityFactor: 8,
                          itemCount: processedFiles.length,
                          itemBuilder: (context, index) {
                            return Container(
                              height: 75,
                              margin: const EdgeInsets.fromLTRB(5, 5, 20, 5),
                              decoration:
                                  neumorphicDecoration(borderRadius: 16),
                              child: ListTile(
                                contentPadding: const EdgeInsets.all(10),
                                title: Text(
                                  processedFiles[index],
                                  style: (ralewayStyle.copyWith(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.blueDarkColor)),
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    Container(
                                      decoration: neumorphicDecoration(
                                          borderRadius: 16),
                                      child: ElevatedButton(
                                        onPressed: () {
                                          _downloadFile(processedFiles[index]);
                                        },
                                        style: ElevatedButton.styleFrom(
                                          padding: EdgeInsets.symmetric(
                                            horizontal: MediaQuery.of(context)
                                                    .size
                                                    .width *
                                                0.01,
                                            vertical: MediaQuery.of(context)
                                                    .size
                                                    .height *
                                                0.02,
                                          ),
                                          shape: RoundedRectangleBorder(
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          backgroundColor:
                                              AppColors.mainBackColor,
                                        ),
                                        child: const Text(
                                          'Download',
                                          style: TextStyle(color: Colors.white),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    IconButton(
                                      icon: const Icon(
                                        Icons.delete,
                                        color: Colors.red,
                                        size: 30,
                                      ),
                                      onPressed: () => {
                                        _deleteProcessFile(
                                            processedFiles[index]),
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
