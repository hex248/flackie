#include <string>
#include <iostream>
#include <vector>
#include <set>
#include <map>

#include <filesystem>
namespace fs = std::filesystem;

#include <taglib/fileref.h>
#include <taglib/tag.h>

inline bool isAudioFile(const fs::path &filePath);
std::set<fs::path> collect(const fs::path &directory, bool directoriesOnly = true);
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

    for (const auto &artistPair : artistMap)
    {
        const std::string &artistName = artistPair.first;
        const std::set<fs::path> &albums = artistPair.second;

        printf("%s\n", artistName.c_str());

        for (const auto &albumPath : albums)
        {
            std::string albumName = albumPath.filename().string();
            printf("  %s\n", albumName.c_str());

            const std::set<fs::path> &tracks = albumMap[albumName];
            for (const auto &track : tracks)
            {
                displayTrackData(track);
            }
        }
    }

    return 0;
}

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