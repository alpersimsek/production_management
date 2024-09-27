import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/user_dashboard.dart';
import 'blocs/auth_bloc.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  await dotenv.load(fileName: ".env");
  runApp(GDPRApp());
}

class GDPRApp extends StatelessWidget {
  final AuthService authService = AuthService();

  GDPRApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (context) => AuthBloc(authService: authService),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'GDPR App',
        home: FutureBuilder<UserModel?>(
          future: authService.autoLogin(), // Check if user has a valid token
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            } else if (snapshot.hasData) {
              // If autoLogin finds a valid token, navigate to UserDashboard
              return UserDashboard(user: snapshot.data!);
            } else {
              // If no valid token, show login screen
              return const LoginScreen();
            }
          },
        ),
      ),
    );
  }
}
