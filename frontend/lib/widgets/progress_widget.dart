import 'package:flutter/material.dart';

class ProgressWidget extends StatelessWidget {
  final double progress; // Progress value between 0.0 to 1.0

  const ProgressWidget({super.key, required this.progress});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            CircularProgressIndicator(
              value: progress, // Set the progress value here
              strokeWidth: 6.0,
              backgroundColor: Colors.grey[300],
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
            Text(
              '${(progress * 100).toInt()}%', // Display the percentage value
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        const Text(
          'Uploading...', // You can change this to "Processing..." for file processing tasks
          style: TextStyle(fontSize: 16),
        ),
      ],
    );
  }
}
