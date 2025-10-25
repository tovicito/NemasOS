import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

void main() {
  runApp(const NeMaps());
}

class NeMaps extends StatelessWidget {
  const NeMaps({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: FlutterMap(
          options: const MapOptions(
            initialCenter: LatLng(51.509364, -0.128928),
            initialZoom: 9.2,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
              userAgentPackageName: 'com.example.nemaps',
            ),
            RichAttributionWidget(
              attributions: const [
                TextSourceAttribution(
                  'Stadia Maps',
                ),
                TextSourceAttribution(
                  'Stamen Design',
                ),
                TextSourceAttribution(
                  'OpenMapTiles',
                ),
                TextSourceAttribution(
                  'OpenStreetMap contributors',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
