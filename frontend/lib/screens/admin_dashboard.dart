import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/add_user_dialog.dart';
import 'package:frontend/screens/gdpr_mask_screen.dart';
import 'package:frontend/screens/login_screen.dart';
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

  @override
  void initState() {
    super.initState();
    fetchUsers(); // Fetch users when the screen loads
  }

  Future<void> fetchUsers() async {
    final response = await http.get(
      Uri.parse('http://localhost:8000/admin/list_users'),
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
        Uri.parse('http://localhost:8000/admin/update_password/$username'),
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
      Uri.parse('http://localhost:8000/admin/delete_user/$username'),
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

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state is AuthInitial) {
          // Navigate to login screen on logout
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => LoginScreen()),
          );
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text(
            'Admin Dashboard',
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
          ),
          leading: IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.security,
              size: 40,
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
                    builder: (context) => LoginScreen(),
                  ),
                );
              },
            ),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(
                height: 30,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'User Management',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _showAddUserDialog,
                    icon: const Icon(Icons.add),
                    label: const Text('Add User'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
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
                      return Card(
                        margin: const EdgeInsets.symmetric(
                            horizontal: 100, vertical: 10),
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(
                              horizontal: 20, vertical: 10),
                          title: Text(
                            user['username'],
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          subtitle: Text(
                            user['role'],
                            style: const TextStyle(color: Colors.grey),
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
                                    child: const Text('Update Pass'),
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
                                    child: const Text('Delete'),
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
