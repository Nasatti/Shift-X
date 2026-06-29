import 'package:http/http.dart' as http;
import 'dart:convert';
import 'models/talk.dart';

Future<List<Talk>> initEmptyList() async {
  Iterable list = json.decode("[]");
  var talks = list.map((model) => Talk.fromJSON(model)).toList();
  return talks;
}

Future<CareerPath> getCareerPath(String jobTitle) async {
  var url = Uri.parse(
    'https://msyavs3hs4.execute-api.us-east-1.amazonaws.com/default/Carrer_Path_Master',
  );

  final http.Response response = await http.post(
    url,
    headers: <String, String>{'Content-Type': 'application/json'},
    body: jsonEncode(<String, Object>{
      'job': jobTitle,
    }),
  );
  if (response.statusCode == 200) {
    final body = utf8.decode(response.bodyBytes);
    final Map<String, dynamic> jsonMap = json.decode(body);
    return CareerPath.fromJSON(jsonMap);
  } else {
    throw Exception('Failed to load career path. Please try again.');
  }
}

Future<List<RelatedVideo>> getWatchNext(String talkId) async {
  var url = Uri.parse(
    'https://e3q93kdqyj.execute-api.us-east-1.amazonaws.com/default/Get_Watch_next',
  );

  final http.Response response = await http.post(
    url,
    headers: <String, String>{'Content-Type': 'application/json'},
    body: jsonEncode(<String, Object>{
      'id': talkId,
    }),
  );
  if (response.statusCode == 200) {
    final body = utf8.decode(response.bodyBytes);
    final Map<String, dynamic> jsonMap = json.decode(body);
    final List<dynamic> jsonList = jsonMap['related_videos'] ?? [];
    return jsonList.map((json) => RelatedVideo.fromJSON(json)).toList();
  } else {
    throw Exception('Failed to load watch next videos');
  }
}
