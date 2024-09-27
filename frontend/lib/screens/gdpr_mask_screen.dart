import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:csv/csv.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_elastic_list_view/flutter_elastic_list_view.dart';
import 'package:frontend/blocs/auth_bloc.dart';
import 'package:frontend/models/user_model.dart';
import 'package:frontend/screens/admin_dashboard.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/styles/app_colors.dart';
import 'package:frontend/screens/styles/app_styles.dart';
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
  String backendUrl = dotenv.env['API_URL'] ?? 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    _fetchGdprMap();
  }

  Future<void> _fetchGdprMap() async {
    try {
      Dio dio = Dio();
      final response = await dio.get(
        '$backendUrl/files/gdpr_map/',
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
    final screenWidth = MediaQuery.of(context).size.width;
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
              Icons.home,
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
                  builder: (context) => const LoginScreen(),
                ),
              );
            },
          ),
        ],
      ),
      backgroundColor: AppColors.greyColor,
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _gdprMapData.isEmpty
              ? const Center(child: Text("No data available"))
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text(
                        "Match Masked Values with Original Values",
                        style: (montserrat.copyWith(
                            fontSize: 30,
                            fontWeight: FontWeight.bold,
                            color: AppColors.blueDarkColor)),
                      ),
                      const SizedBox(height: 20),
                      Container(
                        width: screenWidth * 0.5,
                        decoration: neumorphicDecoration(borderRadius: 16),
                        child: TextField(
                          decoration: InputDecoration(
                            labelText: 'Search',
                            prefixIcon: const Icon(Icons.search),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          onChanged: _filterGdprMap,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.all(20.0),
                          child: ElasticListView.builder(
                            itemCount: _filteredGdprMapData.length,
                            curve: Easing.linear,
                            itemBuilder: (context, index) {
                              final row = _filteredGdprMapData[index];
                              final type = row[0].toString();
                              final original = row[1].toString();
                              final masked = row[2].toString();

                              return Container(
                                padding: const EdgeInsets.all(20),
                                width: screenWidth * 0.5,
                                decoration:
                                    neumorphicDecoration(borderRadius: 2),
                                child: ListTile(
                                  title: SelectableText(
                                    'Type: $type, Original: $original, Masked: $masked',
                                    contextMenuBuilder:
                                        (context, editableTextState) {
                                      return AdaptiveTextSelectionToolbar(
                                        anchors: editableTextState
                                            .contextMenuAnchors,
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
                                    style: (ralewayStyle.copyWith(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18)),
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
                      ),
                    ],
                  ),
                ),
    );
  }
}
