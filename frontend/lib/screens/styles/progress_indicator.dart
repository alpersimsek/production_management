import 'package:flutter/material.dart';

class GradientProgressIndicator extends StatelessWidget {
  final double progress;

  final Color color1;

  final Color color2;

  final Color color3;

  const GradientProgressIndicator(
      {super.key,
      required this.progress,
      required this.color1,
      required this.color2,
      required this.color3});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 30, // Custom height for the progress bar
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20), // Rounded corners
        color: Colors.grey[300], // Background color
      ),
      child: ShaderMask(
        shaderCallback: (Rect bounds) {
          return LinearGradient(
            colors: [color1, color2, color3],
            stops: const [0.0, 0.5, 1.0],
          ).createShader(bounds);
        },
        child: LinearProgressIndicator(
          value: progress,
          minHeight: 30,
          backgroundColor: Colors.transparent, // Transparent background
          borderRadius: BorderRadius.circular(20),
          valueColor: const AlwaysStoppedAnimation<Color>(
              Colors.white), // Set any color here
        ),
      ),
    );
  }
}
