#include "pch.h"
#include "Resources.h"
#include "resources.load.h"
#include "resources/import/resources.import.h"
#include "resources/trackCache.h"
#include "utils/convect.string.h"
#include "resource/version.h"
#include <cstdio>
#include <exception>

Resources::Resources()
{
    PaimonTemplate = TianLi::Resources::Load::load_image("paimon");
    PrimogemTemplate = TianLi::Resources::Load::load_image("star");
    StarTemplate = PrimogemTemplate.clone();
    MinimapCailbTemplate = TianLi::Resources::Load::load_image("cailb");
    UID = TianLi::Resources::Load::load_image("uid_");
    UIDnumber[0] = TianLi::Resources::Load::load_image("uid0");
    UIDnumber[1] = TianLi::Resources::Load::load_image("uid1");
    UIDnumber[2] = TianLi::Resources::Load::load_image("uid2");
    UIDnumber[3] = TianLi::Resources::Load::load_image("uid3");
    UIDnumber[4] = TianLi::Resources::Load::load_image("uid4");
    UIDnumber[5] = TianLi::Resources::Load::load_image("uid5");
    UIDnumber[6] = TianLi::Resources::Load::load_image("uid6");
    UIDnumber[7] = TianLi::Resources::Load::load_image("uid7");
    UIDnumber[8] = TianLi::Resources::Load::load_image("uid8");
    UIDnumber[9] = TianLi::Resources::Load::load_image("uid9");

    cv::cvtColor(StarTemplate, StarTemplate, cv::COLOR_RGB2GRAY);
    cv::cvtColor(UID, UID, cv::COLOR_RGB2GRAY);
    for (int i = 0; i < 10; i++)
    {
        cv::cvtColor(UIDnumber[i], UIDnumber[i], cv::COLOR_RGB2GRAY);
    }
}

std::shared_ptr<Resources> Resources::getSharedPtr()
{
    static std::shared_ptr<Resources> instance(new Resources, [](Resources* p) { delete p; });
    return instance;
}

static void log_load_cache_failure(const std::string& cache_file_path, const char* exception_type, const char* exception_what)
{
    std::error_code ec;
    const auto fsize = std::filesystem::file_size(cache_file_path, ec);
    const auto fsize_str = ec ? "unknown" : std::to_string(fsize);
    bool ifs_ok = false;
    {
        std::ifstream probe(cache_file_path, std::ios::binary | std::ios::ate);
        ifs_ok = probe.good();
        probe.close();
    }

    std::fprintf(stderr,
        "[cache_load_debug] path=\"%s\" size=%s ifstream_ok=%s exception_type=\"%s\" exception_what=\"%s\"\n",
        cache_file_path.c_str(),
        fsize_str.c_str(),
        ifs_ok ? "true" : "false",
        exception_type,
        exception_what);
    std::fflush(stderr);
}

bool load_cache(const std::string& cache_file_path, std::shared_ptr<trackCache::CacheInfo>& cacheInfo)
{
    try
    {
        cacheInfo = trackCache::Deserialize(cache_file_path);
    }
    catch (const std::exception& e)
    {
        log_load_cache_failure(cache_file_path, typeid(e).name(), e.what());
        return false;
    }
    catch (...)
    {
        log_load_cache_failure(cache_file_path, "unknown", "non-std exception");
        return false;
    }
    return true;
}
