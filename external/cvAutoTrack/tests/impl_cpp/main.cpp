#include <Windows.h>
#include <cvAutoTrack.h>
#include <fmt/format.h>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
#ifdef _DEBUG
    #include <filesystem>
#endif

int TEST()
{
    char version_buff[256] = { 0 };
    if (GetCompileVersion(version_buff, 256))
        fmt::print("Version      : {}\n", version_buff);
    else
        fmt::print("Error code   : {}\n", GetLastErr());

    char version_time_buff[256] = { 0 };
    if (GetCompileTime(version_time_buff, 256))
        fmt::print("Build time   : {}\n", version_time_buff);
    else
        fmt::print("Error code   : {}\n", GetLastErr());

    std::cout << "Test complete\n";
    return 0;
}

int TEST_init_and_uninit()
{
    std::cout << "Testing init and uninit\n";

    InitResource();
    Sleep(1000);
    UnInitResource();
    Sleep(1000);
    InitResource();
    Sleep(1000);
    UnInitResource();
    Sleep(1000);
    InitResource();
    Sleep(1000);
    UnInitResource();
    Sleep(1000);

    std::cout << "Test complete\n";
    return 0;
}

void Run_SetDx()
{
    if (SetUseGraphicsCaptureMode())
        fmt::print("DX graphics capture mode enabled\n");
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_SetBit()
{
    if (SetUseBitbltCaptureMode())
    {
        std::cout << "BitBlt capture mode enabled\n";
    }
    else
    {
        std::cout << "Error code   : " << GetLastErr() << "\n";
    }
}

void Run_GetTrans()
{
    double x = 0;
    double y = 0;
    double a = 0;
    int map_id = 0;
    if (GetTransformOfMap(x, y, a, map_id))
        fmt::print("Position and angle: {} {} {} {}\n", x, y, a, map_id);
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_SetUseLocalPictureMode()
{
    if (SetUseLocalPictureMode())
    {
        auto imgFs = std::fstream("test_scene.png", std::ios::in | std::ios::binary);
        size_t size = imgFs.seekg(0, std::ios::end).tellg();
        char* data = new char[size];
        imgFs.seekg(0, std::ios::beg);
        imgFs.read(data, size);
        SetScreenSourceImage(data, size);
        delete[] data;
        fmt::print("Local image mode enabled\n");
    }
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetDir()
{
    double a2 = 0;
    if (GetDirection(a2))
        fmt::print("Character angle: {}\n", a2);
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetRot()
{
    double aa2 = 0;
    if (GetRotation(aa2))
        fmt::print("Camera rotation: {}\n", aa2);
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetAll()
{
    double x, y, a, r;
    int mapId, uid;
    std::string mapType;
    double time_beg = GetTickCount();
    if (GetAllInfo(x, y, mapId, a, r, uid))
    {
        double time_end = GetTickCount();
        switch (mapId)
        {
            case 0: mapType = "Teyvat"; break;
            case 1: mapType = "Enkanomiya"; break;
            case 2: mapType = "The Chasm Underground Mines"; break;
            default: mapType = "Unknown"; break;
        }
        std::cout << fmt::format(R"(
All information:
Area: {}
Position: x = {:6.2f}; y = {:6.2f}
Direction: character = {:4.2f}; camera = {:4.2f}
UID: {:d}
Elapsed: {:4.2f} ms
----------------
)",
                                 mapType, x, y, a, r, uid, time_end - time_beg);
    }
    else
    {
        fmt::print("Error code   : {}\n", GetLastErr());
    }
}

void Run_GetUID()
{
    int uid = 0;
    if (GetUID(uid))
        fmt::print("UID          : {}\n", uid);
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetStars()
{
    fmt::print("GetStar is no longer available.\n");
}

void Run_Capture()
{
    if (DebugCapture())
        fmt::print("Capture succeeded\n");
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetPosit()
{
    int mapid = 0;
    double x2 = 0;
    double y2 = 0;
    if (GetPositionOfMap(x2, y2, mapid))
        fmt::print("Position     : {} {} {}\n", x2, y2, mapid);
    else
        fmt::print("Error code   : {}\n", GetLastErr());
}

void Run_GetVersion()
{
    char* ver = new char[100];
    GetCompileVersion(ver, 100);
    std::cout << ver << std::endl;
    delete[] ver;
}

int RUN(bool is_off_capture = false, bool is_only_capture = false, int frame_rate = 0)
{
    return 0;
}

int Run()
{
    std::ios::sync_with_stdio(false);

#ifdef _DEBUG
    if (std::filesystem::exists("map.jpg"))
    {
        DebugLoadMapImagePath("map.jpg");
    }
    else
    {
        std::cout << "Failed to load test image \"map.jpg\". Feature point visualization will be unavailable." << std::endl;
    }
#endif

    while (1)
    {
        std::cout <<
            R"(
1. Enable DX graphics capture
2. Enable BitBlt capture
3. Get position and angle
4. Get position
5. Get character angle
6. Get camera rotation
7. Get current UID
8. Get current Oculus JSON
9. Capture screenshot
10. Visual debug mode (Debug builds only)
11. Initialize resources
12. Use local image source
=====================
-1. Get version
0. Exit
Enter option:
)";
        int option = 0;
        std::cin >> option;
        std::cout << "\n";
        switch (option)
        {
            case 11:
                InitResource();
                system("pause");
                break;
            case 1:
                Run_SetDx();
                system("pause");
                break;
            case 2:
                Run_SetBit();
                system("pause");
                break;
            case 3:
                Run_GetTrans();
                system("pause");
                break;
            case 4:
                Run_GetPosit();
                system("pause");
                break;
            case 5:
                Run_GetDir();
                system("pause");
                break;
            case 6:
                Run_GetRot();
                system("pause");
                break;
            case 7:
                Run_GetUID();
                system("pause");
                break;
            case 8:
                Run_GetStars();
                system("pause");
                break;
            case 9:
                Run_Capture();
                system("pause");
                break;
            case 10:
                while (1)
                {
                    if (GetAsyncKeyState(VK_ESCAPE) & 0x8000)
                    {
                        break;
                    }
                    Sleep(100);
                    Run_GetAll();
                }
                break;
            case -1:
                Run_GetVersion();
                system("pause");
                break;
            case 0:
                return 0;
            default:
                break;
        }

        std::cout << std::flush;

        Sleep(30);
        system("cls");
    }
    return 0;
}

void HELP()
{
    std::cout << "-help      : show help text\n";
    std::cout << "-test      : run smoke test\n";
    std::cout << "-capture   : configure capture\n";
    std::cout << "    [--off]  : disable capture\n";
    std::cout << "    [--only] : run one capture only\n";
    std::cout << "    [--t int]: set capture frame rate\n";
}

int main(int argc, char* argv[])
{
    std::vector<std::string> args;
    for (int i = 0; i < argc; i++)
    {
        args.push_back(argv[i]);
    }

    if (argc > 1 && strcmp(argv[1], "-test") == 0)
    {
        return TEST();
    }
    else
    {
        return Run();
    }
}

void Test_video()
{
    float x = 0;
    float y = 0;
    float a = 0;
    double x2 = 0;
    double y2 = 0;
    double a2 = 0;
    double aa2 = 0;
    int uid = 0;

    std::vector<std::vector<double>> his;
    char path[256] = { "C:/Users/GengG/source/repos/cvAutoTrack/cvAutoTrack/Picture/001.png" };
    char pathV[256] = { "C:/Users/GengG/source/repos/cvAutoTrack/cvAutoTrack/Video/000.mp4" };
    char pathTxt[256] = { "C:/Users/GengG/source/repos/cvAutoTrack/cvAutoTrack/Video/000.json" };

    if (InitResource())
    {
        // Reserved for manual video tests.
    }

    FILE* fptr = NULL;
    fopen_s(&fptr, "./Output.txt", "w+");
    fmt::print("GetInfoLoadPicture is no longer available.");
    fmt::print("GetInfoLoadPicture is no longer available.");
    fmt::print("GetStarJson is no longer available.");
}
