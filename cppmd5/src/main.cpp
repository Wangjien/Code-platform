#include <iostream>
#include <fstream>
#include <filesystem>
#include <openssl/evp.h>
#include <iomanip>
#include <sstream>
#include <thread>
#include <vector>
#include <mutex>
#include <atomic>
#include <queue>
#include <condition_variable>
#include <chrono>
#include <getopt.h>

namespace fs = std::filesystem;

struct {
    std::mutex output_mutex;
    std::mutex queue_mutex;
    std::mutex progress_mutex;
    std::mutex file_mutex;
    std::condition_variable cv;
    std::queue<fs::path> file_queue;
    std::atomic<bool> done{false};
    std::atomic<int> processed{0};
    int total_files = 0;
} sync_data;

struct Config {
    int threads = std::max(1, static_cast<int>(std::thread::hardware_concurrency()));
    bool verbose = false;
    bool recursive = false;
    size_t buffer_size = 8192;
    fs::path output_file = "MD5.txt";  // 默认输出文件
    fs::path input_file;               // 默认输入文件
};

void print_help(const char* program_name) {
    std::cout << "Usage: " << program_name << " [OPTIONS] [PATH]\n"
              << "Parallel MD5 Calculator with File Output\n\n"
              << "Options:\n"
              << "  -t, --threads NUM    Number of worker threads (default: CPU cores)\n"
              << "  -b, --buffer SIZE    Read buffer size in bytes (default: 8192)\n"
              << "  -r, --recursive      Process directories recursively\n"
              << "  -v, --verbose        Enable verbose output to console\n"
              << "  -o, --output FILE    Output results to specified file (default: MD5.txt)\n"
              << "  -i, --input FILE     Input file to process (default: none)\n"
              << "  -h, --help           Display this help message\n\n"
              << "PATH defaults to current directory if not specified\n";
}

void update_progress() {
    std::lock_guard<std::mutex> lock(sync_data.progress_mutex);
    int processed = sync_data.processed.load();
    float percentage = (sync_data.total_files > 0) ? 
        (processed * 100.0f / sync_data.total_files) : 0.0f;
    
    std::cout << "\rProgress: " << processed << "/" << sync_data.total_files 
              << " (" << std::fixed << std::setprecision(1) << percentage << "%)";
    std::cout.flush();
}

std::string compute_md5(const fs::path& file_path, size_t buffer_size) {
    std::ifstream file(file_path, std::ios::binary);
    if (!file) {
        std::lock_guard<std::mutex> lock(sync_data.output_mutex);
        std::cerr << "\nError opening: " << file_path << std::endl;
        return "";
    }

    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(md_ctx, EVP_md5(), nullptr);

    auto buffer = std::make_unique<unsigned char[]>(buffer_size);
    while (file) {
        file.read(reinterpret_cast<char*>(buffer.get()), buffer_size);
        EVP_DigestUpdate(md_ctx, buffer.get(), file.gcount());
    }

    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len;
    EVP_DigestFinal_ex(md_ctx, digest, &digest_len);
    EVP_MD_CTX_free(md_ctx);

    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < digest_len; ++i) {
        oss << std::setw(2) << static_cast<int>(digest[i]);
    }

    sync_data.processed++;
    update_progress();

    return oss.str();
}

void output_result(const fs::path& file_path, const std::string& md5, const Config& config) {
    std::string result_line = md5 + "  " + file_path.string() + "\n";
    
    if (config.verbose) {
        std::lock_guard<std::mutex> lock(sync_data.output_mutex);
        std::cout << result_line;
    }
    
    if (!config.output_file.empty()) {
        std::lock_guard<std::mutex> lock(sync_data.file_mutex);
        std::ofstream outfile(config.output_file, std::ios::app);
        if (outfile) {
            outfile << result_line;
        } else {
            std::cerr << "\nError writing to output file: " << config.output_file << std::endl;
        }
    }
}

void worker_thread(const Config& config) {
    while (true) {
        fs::path file_path;
        {
            std::unique_lock<std::mutex> lock(sync_data.queue_mutex);
            sync_data.cv.wait(lock, [] { 
                return !sync_data.file_queue.empty() || sync_data.done; 
            });

            if (sync_data.done) break;
            file_path = sync_data.file_queue.front();
            sync_data.file_queue.pop();
        }

        std::string md5 = compute_md5(file_path, config.buffer_size);
        if (!md5.empty()) {
            output_result(file_path, md5, config);
        }
    }
}

void collect_files(const fs::path& input_path, const Config& config) {
    if (fs::is_regular_file(input_path)) {
        sync_data.file_queue.push(input_path);
        sync_data.total_files++;
    } else if (fs::is_directory(input_path)) {
        if (config.recursive) {
            for (const auto& entry : fs::recursive_directory_iterator(input_path)) {
                if (entry.is_regular_file()) {
                    sync_data.file_queue.push(entry.path());
                    sync_data.total_files++;
                }
            }
        } else {
            for (const auto& entry : fs::directory_iterator(input_path)) {
                if (entry.is_regular_file()) {
                    sync_data.file_queue.push(entry.path());
                    sync_data.total_files++;
                }
            }
        }
    }
}

int main(int argc, char* argv[]) {
    Config config;
    int opt;
    
    static struct option long_options[] = {
        {"threads", required_argument, 0, 't'},
        {"recursive", no_argument, 0, 'r'},
        {"verbose", no_argument, 0, 'v'},
        {"buffer", required_argument, 0, 'b'},
        {"output", required_argument, 0, 'o'},
        {"input", required_argument, 0, 'i'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };

    while ((opt = getopt_long(argc, argv, "t:rvb:o:i:h", long_options, nullptr)) != -1) {
        switch (opt) {
            case 't': 
                config.threads = std::stoi(optarg); 
                if (config.threads < 1) {
                    std::cerr << "Error: Thread count must be at least 1\n";
                    return 1;
                }
                break;
            case 'r': config.recursive = true; break;
            case 'v': config.verbose = true; break;
            case 'b': 
                config.buffer_size = std::stoul(optarg); 
                if (config.buffer_size < 128) {
                    std::cerr << "Error: Buffer size must be at least 128 bytes\n";
                    return 1;
                }
                break;
            case 'o': config.output_file = optarg; break;
            case 'i': config.input_file = optarg; break;
            case 'h':
                print_help(argv[0]);
                return 0;
            case '?':
                print_help(argv[0]);
                return 1;
        }
    }

    fs::path input_path = (optind < argc) ? argv[optind] : ".";
    
    // 优先使用-i参数指定的输入文件
    if (!config.input_file.empty()) {
        input_path = config.input_file;
    }

    if (!fs::exists(input_path)) {
        std::cerr << "Error: Path does not exist: " << input_path << "\n";
        return 1;
    }

    // 清空或创建输出文件
    if (!config.output_file.empty()) {
        std::ofstream outfile(config.output_file);
        if (!outfile) {
            std::cerr << "Error: Cannot create output file: " << config.output_file << "\n";
            return 1;
        }
    }

    collect_files(input_path, config);

    if (sync_data.file_queue.empty()) {
        std::cerr << "Error: No files found to process\n";
        return 1;
    }

    std::cout << "Processing " << sync_data.total_files << " files with " 
              << config.threads << " threads...\n";

    std::vector<std::thread> threads;
    for (int i = 0; i < config.threads; ++i) {
        threads.emplace_back(worker_thread, std::cref(config));
    }

    while (sync_data.processed < sync_data.total_files) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        update_progress();
    }

    sync_data.done = true;
    sync_data.cv.notify_all();

    for (auto& thread : threads) {
        thread.join();
    }

    std::cout << "\nCompleted! Results saved to " 
              << (config.output_file.empty() ? "console" : config.output_file.string()) 
              << "\n";
    return 0;
}
