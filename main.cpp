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

std::size_t random_0_to_n(std::size_t n);
inline bool isAudioFile(const fs::path &filePath);
std::set<fs::path> collect(const fs::path &directory, bool directoriesOnly = true);
void displayLibrary(const std::map<std::string, std::set<fs::path>> &artistMap,
                    const std::map<std::string, std::set<fs::path>> &albumMap);
void displayTrackData(const fs::path track);
void playTrack(const fs::path track);
void playTracks(const std::set<fs::path> &tracks);

int main()
{
    printf("flackie\n");

    std::string artistsDirectory = "/home/ob/music/artists";
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

    displayLibrary(artistMap, albumMap);

    auto album = albumMap.begin();
    std::advance(album, random_0_to_n(albumMap.size()));

    printf("Playing album: %s\n", album->first.c_str());
    displayTrackData(*album->second.begin());
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
                    displayTrackData(track);
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

void displayTrackData(const fs::path track)
{
    TagLib::FileRef f(track.c_str());
    TagLib::String trackName = f.tag()->title();
    TagLib::String artistName = f.tag()->artist();
    TagLib::String albumName = f.tag()->album();
    unsigned int trackNumber = f.tag()->track();
    printf("   %d - %s\n", trackNumber, trackName.toCString(true));
}

void playTrack(const fs::path track)
{
    std::string command = "mplayer -vo null -msglevel all=0 \"" + track.string() + "\"";
    system(command.c_str());
}

void playTracks(const std::set<fs::path> &tracks)
{
    std::string command = "mplayer -vo null -msglevel all=0";

    for (const auto &track : tracks)
        command += " \"" + track.string() + "\"";
    system(command.c_str());
}