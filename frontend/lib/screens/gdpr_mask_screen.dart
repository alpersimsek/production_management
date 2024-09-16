import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:csv/csv.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/admin_dashboard.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/user_dashboard.dart';

class GdprMapScreen extends StatefulWidget {
  final UserModel user;

  const GdprMapScreen({super.key, required this.user});

  @override
  _GdprMapScreenState createState() => _GdprMapScreenState();
}

class _GdprMapScreenState extends State<GdprMapScreen> {
  List<List<dynamic>> _gdprMapData = [];
  List<List<dynamic>> _filteredGdprMapData = [];
  bool _loading = true;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _fetchGdprMap();
  }

  Future<void> _fetchGdprMap() async {
    try {
      Dio dio = Dio();
      final response = await dio.get(
        'http://localhost:8000/files/gdpr_map/',
        options: Options(responseType: ResponseType.bytes),
      );

      if (response.statusCode == 200) {
        String csvData = String.fromCharCodes(response.data);

        List<List<dynamic>> csvTable =
            const CsvToListConverter().convert(csvData);

        setState(() {
          _gdprMapData = csvTable;
          _filteredGdprMapData = csvTable;
          _loading = false;
        });
      } else {
        setState(() {
          _loading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Failed to load GDPR map!")),
        );
      }
    } catch (e) {
      setState(() {
        _loading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: $e")),
      );
    }
  }

  void _copyToClipboard(String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Copied to clipboard: $text")),
    );
  }

  void _filterGdprMap(String query) {
    setState(() {
      _searchQuery = query;
      if (query.isEmpty) {
        _filteredGdprMapData = _gdprMapData;
      } else {
        _filteredGdprMapData = _gdprMapData
            .where((row) =>
                row[0].toString().toLowerCase().contains(query.toLowerCase()) ||
                row[1].toString().toLowerCase().contains(query.toLowerCase()) ||
                row[2].toString().toLowerCase().contains(query.toLowerCase()))
            .toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'GDPR Processor',
          style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.security,
              size: 40,
            )),
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
              Icons.home_outlined,
              size: 40,
            ),
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (context) => UserDashboard(
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
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _gdprMapData.isEmpty
              ? const Center(child: Text("No data available"))
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Text(
                        "Select and copy an entry",
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 20),
                      TextField(
                        decoration: InputDecoration(
                          labelText: 'Search',
                          prefixIcon: const Icon(Icons.search),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onChanged: _filterGdprMap,
                      ),
                      const SizedBox(height: 20),
                      Expanded(
                        child: ListView.builder(
                          itemCount: _filteredGdprMapData.length,
                          itemBuilder: (context, index) {
                            final row = _filteredGdprMapData[index];
                            final type = row[0].toString();
                            final original = row[1].toString();
                            final masked = row[2].toString();

                            return Card(
                              margin: const EdgeInsets.symmetric(vertical: 8),
                              child: ListTile(
                                title: SelectableText(
                                  'Type: $type, Original: $original, Masked: $masked',
                                  contextMenuBuilder:
                                      (context, editableTextState) {
                                    return AdaptiveTextSelectionToolbar(
                                      anchors:
                                          editableTextState.contextMenuAnchors,
                                      children: [
                                        TextButton(
                                          onPressed: () {
                                            _copyToClipboard(
                                                'Original: $original, Masked: $masked');
                                            Navigator.pop(
                                                context); // Close context menu
                                          },
                                          child: const Text('Copy'),
                                        ),
                                      ],
                                    );
                                  },
                                  style: const TextStyle(fontSize: 16),
                                ),
                                trailing: IconButton(
                                  icon: const Icon(Icons.copy),
                                  onPressed: () => _copyToClipboard(
                                      'Original: $original, Masked: $masked'),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }
}
