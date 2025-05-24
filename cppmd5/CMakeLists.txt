cmake_minimum_required(VERSION 3.20)
project(cppmd5 VERSION 1.0 LANGUAGES CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 平台特定配置
if(WIN32)
    add_definitions(-D_WIN32_WINNT=0x0A00)
elseif(APPLE)
    set(THREADS_PREFER_PTHREAD_FLAG ON)
    set(CMAKE_FIND_FRAMEWORK LAST)
endif()

# 查找依赖项
find_package(Threads REQUIRED)
find_package(OpenSSL REQUIRED)

# 源文件配置
file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.h")

# 构建目标
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# 包含目录
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 链接库
target_link_libraries(${PROJECT_NAME} PRIVATE
    OpenSSL::SSL
    OpenSSL::Crypto
    Threads::Threads
)

# 安装规则
install(TARGETS ${PROJECT_NAME} DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)
