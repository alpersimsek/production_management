import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/admin_dashboard.dart';
import 'package:frontend/screens/styles/app_colors.dart';
import 'package:frontend/screens/styles/app_styles.dart';
import 'package:frontend/screens/styles/responsive_widget.dart';
import 'package:frontend/screens/user_dashboard.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _userNameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    double height = MediaQuery.of(context).size.height;
    double width = MediaQuery.of(context).size.width;
    return Scaffold(
      backgroundColor: AppColors.backColor,
      body: SizedBox(
        height: height,
        width: width,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            ResponsiveWidget.isSmallScreen(context)
                ? const SizedBox()
                : Expanded(
                    child: Container(
                      height: height,
                      color: AppColors.mainBackColor,
                      child: Center(
                        child: Image.asset(
                          "images/logo2.png",
                          width: width * 0.30,
                          height: height * 0.6,
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  ),
            Expanded(
                child: Container(
              height: height,
              margin: EdgeInsets.symmetric(
                  horizontal: ResponsiveWidget.isSmallScreen(context)
                      ? height * 0.032
                      : height * 0.12),
              color: AppColors.backColor,
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    SizedBox(
                      height: height * 0.2,
                    ),
                    RichText(
                      text: TextSpan(
                        text: "Start Masking",
                        style: lato.copyWith(
                          fontSize: 80,
                          color: AppColors.blueDarkColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    SizedBox(height: height * 0.086),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0),
                      child: Column(
                        children: [
                          const SizedBox(height: 16),
                          TextField(
                            style: ralewayStyle.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                            controller: _userNameController,
                            decoration: InputDecoration(
                              labelText: 'Username',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                              contentPadding: EdgeInsets.symmetric(
                                vertical:
                                    MediaQuery.of(context).size.height * 0.02,
                                horizontal:
                                    MediaQuery.of(context).size.width * 0.05,
                              ),
                              prefixIcon:
                                  const Icon(Icons.person_outline_sharp),
                            ),
                          ),
                          const SizedBox(height: 30),
                          // Password Input Field
                          TextField(
                            controller: _passwordController,
                            decoration: InputDecoration(
                              labelText: 'Password',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                              contentPadding: EdgeInsets.symmetric(
                                vertical:
                                    MediaQuery.of(context).size.height * 0.02,
                                horizontal:
                                    MediaQuery.of(context).size.width * 0.05,
                              ),
                              prefixIcon: const Icon(Icons.lock),
                            ),
                            obscureText: true,
                            onSubmitted: (_) => {
                              context.read<AuthBloc>().add(
                                    AuthLoginEvent(
                                      userName: _userNameController.text,
                                      password: _passwordController.text,
                                    ),
                                  )
                            },
                          ),
                          const SizedBox(height: 30),
                          // Login Button
                          BlocConsumer<AuthBloc, AuthState>(
                            listener: (context, state) {
                              if (state is AuthAuthenticated) {
                                final UserModel user = state.user;
                                if (user.role == 'admin') {
                                  Navigator.pushReplacement(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) =>
                                          AdminDashboard(userMod: user),
                                    ),
                                  );
                                } else {
                                  Navigator.pushReplacement(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) =>
                                          UserDashboard(user: user),
                                    ),
                                  );
                                }
                              } else if (state is AuthError) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(state.message),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              }
                            },
                            builder: (context, state) {
                              if (state is AuthLoading) {
                                return const CircularProgressIndicator();
                              }
                              return ElevatedButton(
                                onPressed: () {
                                  context.read<AuthBloc>().add(
                                        AuthLoginEvent(
                                          userName: _userNameController.text,
                                          password: _passwordController.text,
                                        ),
                                      );
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.mainBackColor,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  padding: EdgeInsets.symmetric(
                                    horizontal:
                                        MediaQuery.of(context).size.width *
                                            0.05,
                                    vertical:
                                        MediaQuery.of(context).size.height *
                                            0.02,
                                  ),
                                ),
                                child: Text(
                                  'Login',
                                  style: (ralewayStyle.copyWith(
                                      fontSize: 22,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.whiteColor)),
                                ),
                              );
                            },
                          ),
                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ))
          ],
        ),
      ),
    );
  }
}
