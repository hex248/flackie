#include <regex>
#include <string>
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <random>

#include <filesystem>
namespace fs = std::filesystem;

#include <taglib/fileref.h>
#include <taglib/tag.h>

#include <laserpants/dotenv/dotenv.h>

std::size_t random_0_to_n(std::size_t n);
inline bool isAudioFile(const fs::path &filePath);
std::set<fs::path> collect(const fs::path &directory, bool directoriesOnly = true);
void displayLibrary(const std::map<std::string, std::set<fs::path>> &artistMap,
                    const std::map<std::string, std::set<fs::path>> &albumMap);
void displayTrackData(const fs::path track, const std::string &prefix = "", const std::string &suffix = "");
void playTrack(const fs::path track);
void playTracks(const std::set<fs::path> &tracks);
void displayProgress(const std::string &line);

int main()
{
    dotenv::init();

    const char *envArtistsDir = std::getenv("ARTISTS_DIRECTORY");
    printf("ARTISTS_DIRECTORY: %s\n", envArtistsDir ? envArtistsDir : "(not set)");
    std::string artistsDirectory = envArtistsDir ? envArtistsDir : "/home/ob/music/artists";
    std::set<fs::path> artists = collect(artistsDirectory);
    std::map<std::string, std::set<fs::path>> artistMap;
    std::map<std::string, std::set<fs::path>> albumMap;

    for (const auto &artist : artists)
    {
        std::string artistName = artist.filename().string();

        std::set<fs::path> albums = collect(artist);
        artistMap.insert_or_assign(artistName, albums);

        for (const auto &album : albums)
        {
            std::string albumName = album.filename().string();

            std::set<fs::path> tracks = collect(album, false);
            albumMap.insert_or_assign(albumName, tracks);
        }
    }

    // displayLibrary(artistMap, albumMap);

    auto album = albumMap.begin();
    std::advance(album, random_0_to_n(albumMap.size()));

    printf("playing album: %s\n", album->first.c_str());
    playTracks(album->second);

    return 0;
}

std::size_t random_0_to_n(std::size_t n)
{
    static std::random_device rd;
    static std::mt19937 gen(rd());
    if (n == 0)
        return 0;
    std::uniform_int_distribution<std::size_t> dist(0, n - 1);
    return dist(gen);
}

auto getRandomMapItem = [](const auto &map)
{
    auto item = map.begin();
    std::advance(item, random_0_to_n(map.size()));
    return item;
};

inline bool isAudioFile(const fs::path &filePath)
{
    static const std::vector<std::string> audioExtensions = {
        ".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a"};

    std::string extension = filePath.extension().string();
    for (const auto &ext : audioExtensions)
    {
        if (extension == ext)
            return true;
    }
    return false;
}

std::set<fs::path> collect(const fs::path &directory, bool directoriesOnly)
{
    std::set<fs::path> elements;
    for (const auto &element : fs::directory_iterator(directory))
    {
        if (directoriesOnly && element.is_directory())
            elements.insert(element.path());

        if (!directoriesOnly && element.is_regular_file() && isAudioFile(element.path()))
            elements.insert(element.path());
    }
    return elements;
}

void displayLibrary(const std::map<std::string, std::set<fs::path>> &artistMap,
                    const std::map<std::string, std::set<fs::path>> &albumMap)
{
    for (const auto &artistPair : artistMap)
    {
        const std::string &artistName = artistPair.first;
        const std::set<fs::path> &albums = artistPair.second;

        printf("%s\n", artistName.c_str());

        for (const auto &albumPath : albums)
        {
            std::string albumName = albumPath.filename().string();
            printf("  %s\n", albumName.c_str());

            auto albumIt = albumMap.find(albumName);
            if (albumIt != albumMap.end())
            {
                const std::set<fs::path> &tracks = albumIt->second;
                for (const auto &track : tracks)
                {
                    displayTrackData(track, "    ");
                }
            }
            else
            {
                printf("    No tracks found for album: %s\n", albumName.c_str());
            }
        }
    }
    printf("\n");
}

void displayTrackData(const fs::path track, const std::string &prefix, const std::string &suffix)
{
    TagLib::FileRef f(track.c_str());
    TagLib::String trackName = f.tag()->title();
    TagLib::String artistName = f.tag()->artist();
    TagLib::String albumName = f.tag()->album();
    unsigned int trackNumber = f.tag()->track();
    if (!prefix.empty())
        printf("%s", prefix.c_str());
    printf("track %d: %s", trackNumber, trackName.toCString(true));
    if (!suffix.empty())
        printf("%s", suffix.c_str());
    else
        printf("\n");
}

void playTrack(const fs::path track)
{
    std::string command = "mplayer -novideo \"" + track.string() + "\"";
    system(command.c_str());
}

void playTracks(const std::set<fs::path> &tracks)
{
    std::string command = "mplayer -novideo";

    for (const auto &track : tracks)
        command += " \"" + track.string() + "\"";

    FILE *fp = popen(command.c_str(), "r");
    if (fp == nullptr)
    {
        perror("popen failed");
        return;
    }

    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), fp) != nullptr)
    {
        // add new line to buffer to ensure it updates as intended
        buffer[sizeof(buffer) - 1] = '\n';

        std::string line(buffer);
        std::transform(line.begin(), line.end(), line.begin(), ::tolower);
        if (line.find("track: ") != std::string::npos)
        {
            size_t start = line.find("track: ") + 7; // length of "track: "
            size_t end = line.find("\n", start);
            std::string trackNumber = line.substr(start, end - start);
            try
            {
                std::size_t idx = std::stoul(trackNumber);
                if (idx > 0)
                    --idx;
                if (idx < tracks.size())
                {
                    auto it = tracks.begin();
                    std::advance(it, idx);
                    displayTrackData(*it, "now playing:\n  ", "\n");
                }
            }
            catch (...)
            {
            }
        }
        else if (line.find("a: ") != std::string::npos)
        {
            displayProgress(line);
        }
    }

    pclose(fp);
}

void displayProgress(const std::string &line)
{
    std::regex pattern(
        R"(a:\s*([\d\.]+)\s*\(([\d\.:]+)\)\s*of\s*([\d\.]+)\s*\(([\d\.:]+)\)\s*([\d\.]+)%)");

    std::smatch match;
    if (std::regex_search(line, match, pattern))
    {
        double secs_elapsed = std::stod(match[1].str());
        double total_secs = std::stod(match[3].str());
        double percent = secs_elapsed / total_secs * 100.0;

        printf("\r%ds/%ds (%d%%)\t\t", (int)secs_elapsed, (int)total_secs, (int)percent);
        fflush(stdout);
    }
    else
    {
        // no match
    }
}