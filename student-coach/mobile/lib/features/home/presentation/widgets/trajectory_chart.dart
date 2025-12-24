import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class TrajectoryChart extends StatelessWidget {
  final List<int> values;
  const TrajectoryChart({super.key, required this.values});
  @override
  Widget build(BuildContext context) {
    final labels = _weekDayLabels(values.length);
    final maxVal = values.isEmpty ? 0 : (values.reduce((a, b) => a > b ? a : b));
    final interval = _axisInterval(maxVal);
    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 24,
                getTitlesWidget: (value, meta) {
                  final i = value.toInt();
                  if (i < 0 || i >= labels.length) return const SizedBox.shrink();
                  return Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(labels[i], style: const TextStyle(fontSize: 10, color: Colors.black54)),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  if (value % interval != 0) return const SizedBox.shrink();
                  return Padding(
                    padding: const EdgeInsets.only(right: 4.0),
                    child: Text('${value.toInt()}', style: const TextStyle(fontSize: 10, color: Colors.black54)),
                  );
                },
              ),
            ),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          gridData: const FlGridData(show: false),
          lineTouchData: LineTouchData(
            enabled: true,
            touchTooltipData: LineTouchTooltipData(
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  final minutes = spot.y.toInt();
                  return LineTooltipItem('$minutes min', const TextStyle(color: Colors.white));
                }).toList();
              },
            ),
          ),
          lineBarsData: [
            LineChartBarData(
              isCurved: true,
              color: Colors.indigo,
              barWidth: 3,
              spots: [
                for (var i = 0; i < values.length; i++) FlSpot(i.toDouble(), values[i].toDouble())
              ],
            ),
          ],
        ),
      ),
    );
  }

  List<String> _weekDayLabels(int len) {
    final now = DateTime.now();
    final start = now.subtract(Duration(days: len - 1));
    const names = ['L', 'M', 'M', 'J', 'V', 'S', 'D']; // French initials
    final labels = <String>[];
    for (int i = 0; i < len; i++) {
      final d = start.add(Duration(days: i));
      labels.add(names[(d.weekday - 1) % 7]);
    }
    return labels;
  }

  double _axisInterval(int maxVal) {
    if (maxVal <= 20) return 5;
    if (maxVal <= 50) return 10;
    if (maxVal <= 100) return 20;
    return 50;
  }
}
