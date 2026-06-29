import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'talk_repository.dart';
import 'models/talk.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ShiftX',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFFE50914),
        scaffoldBackgroundColor: const Color(0xFF090505),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFE50914),
          secondary: Color(0xFFB81D24),
          surface: Color(0xFF160D0D),
          onPrimary: Colors.white,
          onSurface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF160D0D),
          elevation: 4,
          shadowColor: Color(0x33FF0000),
          centerTitle: true,
          titleTextStyle: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
            color: Colors.white,
          ),
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1E1111),
          elevation: 8,
          shadowColor: const Color(0x22E50914),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFF3D1414), width: 1.5),
          ),
        ),
        chipTheme: const ChipThemeData(
          backgroundColor: Color(0xFF2C1515),
          disabledColor: Colors.black,
          selectedColor: Color(0xFFE50914),
          secondarySelectedColor: Color(0xFFB81D24),
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          labelStyle: TextStyle(color: Colors.white, fontSize: 11),
          brightness: Brightness.dark,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Color(0xFF160D0D),
          selectedItemColor: Color(0xFFE50914),
          unselectedItemColor: Colors.grey,
          elevation: 8,
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  CareerPath? _currentCareerPath;
  final List<String> _recentSearches = [];

  void _onCareerPathGenerated(CareerPath path, String query) {
    setState(() {
      _currentCareerPath = path;
      if (query.isNotEmpty && !_recentSearches.contains(query)) {
        _recentSearches.insert(0, query);
        if (_recentSearches.length > 5) {
          _recentSearches.removeLast();
        }
      }
      _currentIndex = 1; // Switch to Playlist tab automatically
    });
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      SearchTab(
        recentSearches: _recentSearches,
        onCareerPathGenerated: _onCareerPathGenerated,
      ),
      PlaylistTab(
        careerPath: _currentCareerPath,
      ),
    ];

    return Scaffold(
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: screens[_currentIndex],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.search_rounded),
            activeIcon: Icon(Icons.search_rounded, color: Color(0xFFE50914)),
            label: 'Cerca',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.video_library_rounded),
            activeIcon: Icon(Icons.video_library_rounded, color: Color(0xFFE50914)),
            label: 'La tua Playlist',
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TAB 1: RICERCA DEL RUOLO
// ─────────────────────────────────────────────────────────────────────────────
class SearchTab extends StatefulWidget {
  final List<String> recentSearches;
  final Function(CareerPath, String) onCareerPathGenerated;

  const SearchTab({
    super.key,
    required this.recentSearches,
    required this.onCareerPathGenerated,
  });

  @override
  State<SearchTab> createState() => _SearchTabState();
}

class _SearchTabState extends State<SearchTab> {
  final TextEditingController _controller = TextEditingController();
  Future<CareerPath>? _searchFuture;
  bool _hasSearched = false;

  void _runSearch(String query) {
    final cleanQuery = query.trim();
    if (cleanQuery.isEmpty) return;
    setState(() {
      _hasSearched = true;
      _searchFuture = getCareerPath(cleanQuery);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Career Coach'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            if (!_hasSearched) ...[
              const Spacer(flex: 1),
              Image.asset(
                'logo/X.png',
                height: 140,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 24),
              const Text(
                'Scrivi il tuo ruolo target in inglese. L\'algoritmo intelligente analizzerà le competenze richieste e creerà un corso personalizzato di TEDx Talk.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
              const SizedBox(height: 24),
            ],
            
            // Job Input Box
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1E1111),
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: const Color(0xFF3D1414), width: 1.5),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  const Icon(Icons.work_outline_rounded, color: Colors.grey),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Inserisci il ruolo in inglese (es. data analyst)',
                        hintStyle: TextStyle(color: Colors.grey, fontSize: 14),
                        border: InputBorder.none,
                      ),
                      style: const TextStyle(color: Colors.white),
                      onSubmitted: (val) => _runSearch(val),
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => _runSearch(_controller.text),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFE50914),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                    child: const Text('Genera', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 20),
            
            if (_hasSearched && _searchFuture != null)
              Expanded(
                child: FutureBuilder<CareerPath>(
                  future: _searchFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const CircularProgressIndicator(
                              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFE50914)),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              "Il sistema sta analizzando le competenze per il ruolo di '${_controller.text}'...",
                              textAlign: TextAlign.center,
                              style: const TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                            ),
                          ],
                        ),
                      );
                    } else if (snapshot.hasError) {
                      return Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.error_outline_rounded, size: 60, color: Color(0xFFB81D24)),
                            const SizedBox(height: 12),
                            Text(
                              "Errore di elaborazione:\n${snapshot.error}",
                              textAlign: TextAlign.center,
                              style: const TextStyle(color: Colors.grey),
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () => _runSearch(_controller.text),
                              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFE50914)),
                              child: const Text('Riprova'),
                            )
                          ],
                        ),
                      );
                    } else if (snapshot.hasData) {
                      final cp = snapshot.data!;
                      WidgetsBinding.instance.addPostFrameCallback((_) {
                        widget.onCareerPathGenerated(cp, _controller.text);
                        setState(() {
                          _hasSearched = false;
                          _searchFuture = null;
                        });
                      });
                      return const Center(
                        child: CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFE50914)),
                        ),
                      );
                    }
                    return const SizedBox.shrink();
                  },
                ),
              ),

            if (!_hasSearched) ...[
              if (widget.recentSearches.isNotEmpty) ...[
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
                    child: Text(
                      'Ricerche recenti:',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.grey),
                    ),
                  ),
                ),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: widget.recentSearches.map((search) {
                    return ActionChip(
                      avatar: const Icon(Icons.history_rounded, size: 14, color: Colors.grey),
                      label: Text(search),
                      onPressed: () {
                        _controller.text = search;
                        _runSearch(search);
                      },
                      backgroundColor: const Color(0xFF1E1111),
                      side: const BorderSide(color: Color(0xFF3D1414)),
                    );
                  }).toList(),
                ),
              ],
              const Spacer(flex: 2),
            ],
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TAB 2: PLAYLIST CONSIGLIATA
// ─────────────────────────────────────────────────────────────────────────────
class PlaylistTab extends StatefulWidget {
  final CareerPath? careerPath;

  const PlaylistTab({
    super.key,
    required this.careerPath,
  });

  @override
  State<PlaylistTab> createState() => _PlaylistTabState();
}

class _PlaylistTabState extends State<PlaylistTab> {
  String? _selectedFilterTag;
  String _sortBy = 'default'; // 'default', 'scoreDesc', 'durationAsc', 'durationDesc'

  @override
  void didUpdateWidget(covariant PlaylistTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.careerPath != oldWidget.careerPath) {
      _selectedFilterTag = null;
      _sortBy = 'default';
    }
  }

  @override
  Widget build(BuildContext context) {
    final cp = widget.careerPath;

    if (cp == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('La tua Playlist'),
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Opacity(
                  opacity: 0.2,
                  child: Image.asset(
                    'logo/X.png',
                    height: 100,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Nessun percorso generato',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.grey),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Inserisci un ruolo lavorativo nella scheda "Cerca" per ricevere e visualizzare qui la tua playlist formativa.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey, fontSize: 14),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // Process playlist
    List<Talk> talks = List.from(cp.playlist);

    // Client-side filtering
    if (_selectedFilterTag != null) {
      talks = talks.where((talk) {
        final lowerTag = _selectedFilterTag!.toLowerCase();
        final matchesKeyphrase = talk.keyPhrases.any((phrase) => phrase.toLowerCase().contains(lowerTag));
        final matchesCategory = talk.bestCategory.toLowerCase().contains(lowerTag);
        return matchesKeyphrase || matchesCategory;
      }).toList();
    }

    // Client-side sorting
    if (_sortBy == 'scoreDesc') {
      talks.sort((a, b) => b.score.compareTo(a.score));
    } else if (_sortBy == 'durationAsc') {
      talks.sort((a, b) {
        final durationA = int.tryParse(a.duration) ?? 0;
        final durationB = int.tryParse(b.duration) ?? 0;
        return durationA.compareTo(durationB);
      });
    } else if (_sortBy == 'durationDesc') {
      talks.sort((a, b) {
        final durationA = int.tryParse(a.duration) ?? 0;
        final durationB = int.tryParse(b.duration) ?? 0;
        return durationB.compareTo(durationA);
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('La tua Playlist'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Career Info Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome_rounded, color: Colors.amber),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            "Ruolo Generato: ${cp.job.toUpperCase()}",
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "Categoria: ${cp.category.replaceAll('_', ' ').toUpperCase()}",
                      style: const TextStyle(fontSize: 13, color: Color(0xFFE50914), fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      "Filtra per competenza chiave:",
                      style: TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: cp.tags.map((tag) {
                        final isSelected = _selectedFilterTag == tag;
                        return ChoiceChip(
                          label: Text(tag),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              _selectedFilterTag = selected ? tag : null;
                            });
                          },
                          selectedColor: const Color(0xFFE50914),
                          backgroundColor: const Color(0xFF2C1515),
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : Colors.grey[300],
                            fontSize: 11,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                          side: BorderSide(
                            color: isSelected ? const Color(0xFFE50914) : const Color(0xFF5A1818),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // Header for recommended list and Sort
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    _selectedFilterTag == null
                        ? "Playlist Formativa (${talks.length} Talk)"
                        : "Talk filtrati per $_selectedFilterTag (${talks.length})",
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ),
                PopupMenuButton<String>(
                  icon: const Icon(Icons.sort_rounded, color: Colors.grey, size: 22),
                  tooltip: 'Ordina Playlist',
                  onSelected: (value) {
                    setState(() {
                      _sortBy = value;
                    });
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'default',
                      child: Row(
                        children: [
                          Icon(Icons.star_half_rounded, size: 18),
                          SizedBox(width: 8),
                          Text('Consigliato'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'scoreDesc',
                      child: Row(
                        children: [
                          Icon(Icons.star_rounded, color: Color(0xFFE50914), size: 18),
                          SizedBox(width: 8),
                          Text('Score (Decrescente)'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'durationAsc',
                      child: Row(
                        children: [
                          Icon(Icons.arrow_upward_rounded, size: 18),
                          SizedBox(width: 8),
                          Text('Durata più breve'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'durationDesc',
                      child: Row(
                        children: [
                          Icon(Icons.arrow_downward_rounded, size: 18),
                          SizedBox(width: 8),
                          Text('Durata più lunga'),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            Expanded(
              child: talks.isEmpty
                  ? const Center(
                      child: Text(
                        "Nessun talk corrisponde alla competenza selezionata.",
                        style: TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    )
                  : ListView.builder(
                      physics: const ClampingScrollPhysics(),
                      itemCount: talks.length,
                      itemBuilder: (context, index) {
                        final talk = talks[index];
                        return TalkCard(talk: talk, showScore: true);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENTE: TALK CARD
// ─────────────────────────────────────────────────────────────────────────────
class TalkCard extends StatelessWidget {
  final Talk talk;
  final bool showScore;

  const TalkCard({super.key, required this.talk, this.showScore = false});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => TalkDetailScreen(talk: talk),
            ),
          );
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Talk Cover image (fallback if error)
            ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
              child: Stack(
                children: [
                  Image.network(
                    talk.imageUrl,
                    height: 160,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Container(
                      height: 160,
                      color: const Color(0xFF2C1515),
                      child: const Center(
                        child: Icon(Icons.video_library_rounded, size: 50, color: Color(0xFFE50914)),
                      ),
                    ),
                  ),
                  // Score Indicator
                  if (showScore && talk.score > 0)
                    Positioned(
                      top: 12,
                      right: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xE6E50914),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.star_rounded, color: Colors.white, size: 14),
                            const SizedBox(width: 4),
                            Text(
                              'Score: ${talk.score}',
                              style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ),
                  // Duration Indicator
                  Positioned(
                    bottom: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.75),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        _formatDuration(talk.duration),
                        style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Content
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    talk.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.person_rounded, size: 14, color: Color(0xFFE50914)),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          talk.mainSpeaker,
                          style: const TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  
                  // Key phrases/tags
                  if (talk.keyPhrases.isNotEmpty)
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: talk.keyPhrases.take(4).map((phrase) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFF160D0D),
                            border: Border.all(color: const Color(0xFF3D1414)),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            phrase,
                            style: const TextStyle(fontSize: 10, color: Colors.grey),
                          ),
                        );
                      }).toList(),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDuration(String durationInSeconds) {
    final seconds = int.tryParse(durationInSeconds);
    if (seconds == null) return durationInSeconds;
    final int m = seconds ~/ 60;
    final int s = seconds % 60;
    return "$m:${s.toString().padLeft(2, '0')} min";
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SCHERMATA: DETTAGLIO TALK & WATCH NEXT
// ─────────────────────────────────────────────────────────────────────────────
class TalkDetailScreen extends StatefulWidget {
  final Talk talk;

  const TalkDetailScreen({super.key, required this.talk});

  @override
  State<TalkDetailScreen> createState() => _TalkDetailScreenState();
}

class _TalkDetailScreenState extends State<TalkDetailScreen> {
  late Future<List<RelatedVideo>> _watchNextFuture;

  @override
  void initState() {
    super.initState();
    _watchNextFuture = getWatchNext(widget.talk.id);
  }

  Future<void> _launchVideo() async {
    final Uri url = Uri.parse(widget.talk.url);
    try {
      if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
        throw Exception('Could not launch ${widget.talk.url}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Impossibile aprire il browser per riprodurre il video: $e"),
            backgroundColor: const Color(0xFFB81D24),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dettaglio Talk'),
      ),
      body: SingleChildScrollView(
        physics: const ClampingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Hero Banner
            Stack(
              alignment: Alignment.bottomLeft,
              children: [
                Image.network(
                  widget.talk.imageUrl,
                  height: 220,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Container(
                    height: 220,
                    color: const Color(0xFF2C1515),
                    child: const Center(
                      child: Icon(Icons.video_library_rounded, size: 60, color: Color(0xFFE50914)),
                    ),
                  ),
                ),
                // Gradient Overlay
                Container(
                  height: 220,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black.withValues(alpha: 0.9),
                      ],
                    ),
                  ),
                ),
                // Play Button overlay
                Center(
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 20),
                    child: IconButton(
                      icon: const Icon(Icons.play_circle_fill_rounded, size: 70, color: Color(0xFFE50914)),
                      onPressed: _launchVideo,
                    ),
                  ),
                ),
              ],
            ),
            
            // Detail details
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.talk.title,
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  
                  // Speaker & Meta Info
                  Row(
                    children: [
                      const Icon(Icons.person_rounded, color: Color(0xFFE50914), size: 16),
                      const SizedBox(width: 6),
                      Text(
                        widget.talk.mainSpeaker,
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      const Spacer(),
                      const Icon(Icons.access_time_rounded, color: Colors.grey, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        "${(int.tryParse(widget.talk.duration) ?? 0) ~/ 60} min",
                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Watch Now CTA Button
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton.icon(
                      onPressed: _launchVideo,
                      icon: const Icon(Icons.open_in_new_rounded),
                      label: const Text('Guarda il Talk su TED.com', style: TextStyle(fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFE50914),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  const Divider(color: Color(0xFF3D1414), thickness: 1.5),
                  const SizedBox(height: 12),
                  
                  const Text(
                    'Descrizione',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    widget.talk.details,
                    style: const TextStyle(color: Colors.grey, fontSize: 14, height: 1.4),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Keyword tags
                  if (widget.talk.keyPhrases.isNotEmpty) ...[
                    const Text(
                      'Competenze e Tag Associati',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: widget.talk.keyPhrases.map((phrase) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E1111),
                            border: Border.all(color: const Color(0xFF3D1414)),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            phrase,
                            style: const TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                  ],
                  
                  const Divider(color: Color(0xFF3D1414), thickness: 1.5),
                  const SizedBox(height: 12),
                  
                  // Watch Next Section
                  const Text(
                    'Guarda Anche (Watch Next)',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  
                  FutureBuilder<List<RelatedVideo>>(
                    future: _watchNextFuture,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(
                          child: Padding(
                            padding: EdgeInsets.symmetric(vertical: 20),
                            child: CircularProgressIndicator(
                              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFE50914)),
                            ),
                          ),
                        );
                      } else if (snapshot.hasError) {
                        return Text(
                          "Impossibile caricare i consigliati: ${snapshot.error}",
                          style: const TextStyle(color: Colors.grey, fontSize: 13),
                        );
                      } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                        return const Text(
                          "Nessun talk consigliato disponibile.",
                          style: TextStyle(color: Colors.grey, fontSize: 13),
                        );
                      }
                      
                      final relatedVideos = snapshot.data!;
                      return ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: relatedVideos.length,
                        itemBuilder: (context, idx) {
                          final rel = relatedVideos[idx];
                          return Card(
                            color: const Color(0xFF160D0D),
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: const Icon(Icons.play_arrow_rounded, color: Color(0xFFE50914)),
                              title: Text(
                                rel.title,
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              subtitle: Text(
                                "${rel.speaker}  ·  ${(int.tryParse(rel.duration) ?? 0) ~/ 60} min",
                                style: const TextStyle(fontSize: 11, color: Colors.grey),
                              ),
                              trailing: const Icon(Icons.open_in_new_rounded, size: 16, color: Colors.grey),
                              onTap: () async {
                                // Launch external browser directly for watch next videos
                                final String tedUrl = "https://www.ted.com/talks/${rel.slug}";
                                final Uri uri = Uri.parse(tedUrl);
                                try {
                                  if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
                                    throw Exception('Could not launch $tedUrl');
                                  }
                                } catch (e) {
                                  if (mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text("Impossibile aprire il video: $e")),
                                    );
                                  }
                                }
                              },
                            ),
                          );
                        },
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
