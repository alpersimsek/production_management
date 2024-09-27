import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/add_user_dialog.dart';
import 'package:frontend/screens/gdpr_mask_screen.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/styles/app_colors.dart';
import 'package:frontend/screens/styles/app_styles.dart';
import 'package:frontend/screens/user_dashboard.dart';
import 'package:frontend/widgets/app_drawer.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AdminDashboard extends StatefulWidget {
  final UserModel userMod;
  const AdminDashboard({super.key, required this.userMod});

  @override
  _AdminDashboardState createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  List users = [];
  final String role = 'admin'; // Set role to 'admin' for this screen
  String backendUrl = dotenv.env['API_URL'] ?? 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    fetchUsers(); // Fetch users when the screen loads
  }

  Future<void> fetchUsers() async {
    final response = await http.get(
      Uri.parse('$backendUrl/admin/list_users'),
    );

    if (response.statusCode == 200) {
      setState(() {
        users = jsonDecode(response.body)
            .where((user) => user['username'] != 'admin')
            .toList();
      });
    } else {
      throw Exception('Failed to load users');
    }
  }

  void _showAddUserDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AddUserDialog(onUserAdded: fetchUsers);
      },
    );
  }

  Future<void> _updatePassword(String username) async {
    String newPassword = await _showUpdatePasswordDialog(username);
    if (newPassword.isNotEmpty) {
      final response = await http.put(
        Uri.parse('$backendUrl/admin/update_password/$username'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'password': newPassword}),
      );
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text("Password updated!")));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Failed to update password.")));
      }
    }
  }

  Future<String> _showUpdatePasswordDialog(String username) async {
    String password = '';
    await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(
            "Update Password for $username",
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          content: TextField(
            decoration: const InputDecoration(labelText: "New Password"),
            onChanged: (value) {
              password = value;
            },
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text("Cancel"),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(password);
              },
              child: const Text("Update"),
            ),
          ],
        );
      },
    );
    return password;
  }

  Future<void> _deleteUser(String username) async {
    final response = await http.delete(
      Uri.parse('$backendUrl/admin/delete_user/$username'),
    );

    if (response.statusCode == 200) {
      setState(() {
        users.removeWhere((user) => user['username'] == username);
      });
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text("User deleted!")));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Failed to delete user.")));
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
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state is AuthInitial) {
          // Navigate to login screen on logout
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const LoginScreen()),
          );
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.grey.shade200,
          title: Text(
            'Admin Dashboard',
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
            IconButton(
              icon: const Icon(
                Icons.cloud_upload,
                size: 40,
              ),
              onPressed: () {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(
                    builder: (context) => UserDashboard(
                      user: widget.userMod,
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
                      user: widget.userMod,
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
                    builder: (context) => const LoginScreen(),
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(
                height: 30,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Text(
                    'User Management',
                    style: (montserrat.copyWith(
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        color: AppColors.blueDarkColor)),
                  ),
                  ElevatedButton(
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
                    onPressed: _showAddUserDialog,
                    child: Row(
                      mainAxisSize: MainAxisSize
                          .min, // Keep the button tight to the content
                      children: [
                        const Icon(
                          Icons.add,
                          size: 30,
                          color: Colors.white,
                        ),
                        const SizedBox(
                            width: 8), // Add space between image and text
                        Text(
                          'Add New User',
                          style: (ralewayStyle.copyWith(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: AppColors.whiteColor)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 8,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: ListView.builder(
                    itemCount: users.length,
                    itemBuilder: (context, index) {
                      final user = users[index];
                      return Container(
                        decoration: neumorphicDecoration(borderRadius: 16),
                        margin: const EdgeInsets.symmetric(
                            horizontal: 100, vertical: 10),
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(
                              horizontal: 20, vertical: 10),
                          title: Text(
                            user['username'],
                            style: (ralewayStyle.copyWith(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textColor)),
                          ),
                          subtitle: Text(
                            user['role'],
                            style: (ralewayStyle.copyWith(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: AppColors.mainBlueColor)),
                          ),
                          trailing: SizedBox(
                            width: 300,
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                Expanded(
                                  child: TextButton(
                                    onPressed: () =>
                                        _updatePassword(user['username']),
                                    style: TextButton.styleFrom(
                                      foregroundColor: Colors.blueAccent,
                                    ),
                                    child: Text(
                                      'Update Pass',
                                      style: (ralewayStyle.copyWith(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                          color: AppColors.textColor)),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: TextButton(
                                    onPressed: () =>
                                        _deleteUser(user['username']),
                                    style: TextButton.styleFrom(
                                      foregroundColor: Colors.redAccent,
                                    ),
                                    child: Text(
                                      'Delete',
                                      style: (ralewayStyle.copyWith(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      )),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
