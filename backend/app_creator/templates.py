def generate_main_dart(app_path, app_name):
    content = f"""
import 'package:flutter/material.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("{app_name}")),
        body: Center(child: Text("Hello {app_name} 🚀")),
      ),
    );
  }}
}}
"""
    with open(app_path / "lib/main.dart", "w") as f:
        f.write(content)


def generate_pubspec(app_path, app_name):
    content = f"""
name: {app_name}
description: Generated App

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
"""
    with open(app_path / "pubspec.yaml", "w") as f:
        f.write(content)