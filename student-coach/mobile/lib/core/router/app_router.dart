import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';

final appRouterProvider = Provider<RouterConfig<Object>>((ref) {
  return RouterConfig(
    routerDelegate: _AppRouterDelegate(),
    routeInformationParser: _AppRouteParser(),
    routeInformationProvider: PlatformRouteInformationProvider(
      initialRouteInformation: const RouteInformation(location: '/'),
    ),
  );
});

class _AppRouterDelegate extends RouterDelegate<Object> with ChangeNotifier, PopNavigatorRouterDelegateMixin<Object> {
  @override
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  final bool _loggedIn = false;

  @override
  Widget build(BuildContext context) {
    return Navigator(
      key: navigatorKey,
      pages: [
        if (!_loggedIn) const MaterialPage(child: LoginScreen()) else const MaterialPage(child: HomeScreen()),
      ],
      onPopPage: (route, result) => route.didPop(result),
    );
  }

  @override
  Future<void> setNewRoutePath(Object configuration) async {}
}

class _AppRouteParser extends RouteInformationParser<Object> {
  @override
  Future<Object> parseRouteInformation(RouteInformation routeInformation) async {
    // Return a simple configuration based on location; not used heavily by our delegate
    return routeInformation.location ?? '/';
  }

  @override
  RouteInformation? restoreRouteInformation(Object configuration) {
    return RouteInformation(location: configuration.toString());
  }
}
