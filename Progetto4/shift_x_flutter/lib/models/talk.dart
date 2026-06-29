class Talk {
  final String id;
  final String slug;
  final String title;
  final String details;
  final String mainSpeaker;
  final String url;
  final String imageUrl;
  final String duration;
  final String publishedAt;
  final List<String> keyPhrases;
  final String bestCategory;
  final int score;

  Talk({
    required this.id,
    required this.slug,
    required this.title,
    required this.details,
    required this.mainSpeaker,
    required this.url,
    required this.imageUrl,
    required this.duration,
    required this.publishedAt,
    required this.keyPhrases,
    required this.bestCategory,
    required this.score,
  });

  factory Talk.fromJSON(Map<String, dynamic> jsonMap) {
    // Determine the id (can be _id or id)
    final String parsedId = (jsonMap['_id'] ?? jsonMap['id'] ?? "").toString();
    
    // Determine title
    final String parsedTitle = jsonMap['title'] ?? "";
    
    // Determine description/details
    final String parsedDetails = jsonMap['description'] ?? jsonMap['details'] ?? "";
    
    // Determine speaker
    final String parsedSpeaker = (jsonMap['speakers'] ?? jsonMap['speaker'] ?? jsonMap['mainSpeaker'] ?? "").toString();
    
    // Determine url
    final String parsedUrl = (jsonMap['url'] ?? "").toString();
    
    // Determine image url, providing a fallback to a nice placeholder if empty
    String parsedImageUrl = (jsonMap['image_url'] ?? "").toString();
    if (parsedImageUrl.isEmpty) {
      // Use a premium looking TEDx image as fallback
      parsedImageUrl = "https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=600&auto=format&fit=crop";
    }
    
    // Determine duration
    final String parsedDuration = (jsonMap['duration'] ?? "").toString();
    
    // Determine published date
    final String parsedPublishedAt = (jsonMap['publishedAt'] ?? "").toString();
    
    // Determine best category
    final String parsedBestCategory = (jsonMap['best_category'] ?? jsonMap['category'] ?? "").toString();
    
    // Determine score
    final int parsedScore = int.tryParse((jsonMap['score'] ?? "0").toString()) ?? 0;

    // Determine keyphrases
    List<String> parsedKeyPhrases = [];
    if (jsonMap['comprehend_analysis'] != null && jsonMap['comprehend_analysis']['KeyPhrases'] != null) {
      final kp = jsonMap['comprehend_analysis']['KeyPhrases'];
      if (kp is List) {
        parsedKeyPhrases = kp.map((e) => e.toString()).toList();
      }
    }
    
    // Fallback to tags or skills if keyphrases is empty
    if (parsedKeyPhrases.isEmpty) {
      if (jsonMap['tags'] != null && jsonMap['tags'] is List) {
        parsedKeyPhrases = (jsonMap['tags'] as List).map((e) => e.toString()).toList();
      } else if (jsonMap['skills'] != null && jsonMap['skills'] is List) {
        parsedKeyPhrases = (jsonMap['skills'] as List).map((e) => e.toString()).toList();
      }
    }

    return Talk(
      id: parsedId,
      slug: jsonMap['slug'] ?? "",
      title: parsedTitle,
      details: parsedDetails,
      mainSpeaker: parsedSpeaker,
      url: parsedUrl,
      imageUrl: parsedImageUrl,
      duration: parsedDuration,
      publishedAt: parsedPublishedAt,
      keyPhrases: parsedKeyPhrases,
      bestCategory: parsedBestCategory,
      score: parsedScore,
    );
  }
}

class RelatedVideo {
  final String id;
  final String slug;
  final String title;
  final String speaker;
  final String duration;

  RelatedVideo({
    required this.id,
    required this.slug,
    required this.title,
    required this.speaker,
    required this.duration,
  });

  factory RelatedVideo.fromJSON(Map<String, dynamic> jsonMap) {
    return RelatedVideo(
      id: (jsonMap['id'] ?? jsonMap['_id'] ?? "").toString(),
      slug: (jsonMap['slug'] ?? "").toString(),
      title: (jsonMap['title'] ?? "").toString(),
      speaker: (jsonMap['speaker'] ?? jsonMap['speakers'] ?? "").toString(),
      duration: (jsonMap['duration'] ?? "").toString(),
    );
  }
}

class CareerPath {
  final String job;
  final String category;
  final List<String> tags;
  final int count;
  final List<Talk> playlist;

  CareerPath({
    required this.job,
    required this.category,
    required this.tags,
    required this.count,
    required this.playlist,
  });

  factory CareerPath.fromJSON(Map<String, dynamic> json) {
    final List<dynamic> rawPlaylist = json['playlist'] ?? [];
    return CareerPath(
      job: json['job'] ?? "",
      category: json['category'] ?? "",
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      count: json['count'] ?? 0,
      playlist: rawPlaylist.map((item) => Talk.fromJSON(item)).toList(),
    );
  }
}
