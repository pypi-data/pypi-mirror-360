#include <atomic>
#include <chrono>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <ios>
#include <iostream>
#include <mutex>
#include <string>
#include <string_view>

#include <networkit/GlobalState.hpp>
#include <networkit/auxiliary/Log.hpp>

namespace Aux {
namespace Log {

void setLogLevel(std::string_view logLevel) {
    if (logLevel == "TRACE") {
        NetworKit::GlobalState::setLogLevel(LogLevel::TRACE);
    } else if (logLevel == "DEBUG") {
        NetworKit::GlobalState::setLogLevel(LogLevel::DEBUG);
    } else if (logLevel == "INFO") {
        NetworKit::GlobalState::setLogLevel(LogLevel::INFO);
    } else if (logLevel == "WARN") {
        NetworKit::GlobalState::setLogLevel(LogLevel::WARN);
    } else if (logLevel == "ERROR") {
        NetworKit::GlobalState::setLogLevel(LogLevel::ERROR);
    } else if (logLevel == "FATAL") {
        NetworKit::GlobalState::setLogLevel(LogLevel::FATAL);
    } else if (logLevel == "QUIET") {
        NetworKit::GlobalState::setLogLevel(LogLevel::QUIET);
    } else {
        throw std::runtime_error("unknown loglevel");
    }
}

std::string getLogLevel() {
    LogLevel current = NetworKit::GlobalState::getLogLevel();
    switch (current) {
    case LogLevel::TRACE:
        return "TRACE";
    case LogLevel::DEBUG:
        return "DEBUG";
    case LogLevel::INFO:
        return "INFO";
    case LogLevel::WARN:
        return "WARN";
    case LogLevel::ERROR:
        return "ERROR";
    case LogLevel::FATAL:
        return "FATAL";
    case LogLevel::QUIET:
        return "QUIET";
    default:
        throw std::logic_error{"invalid loglevel in getLogLevel()"};
    }
}

void printLogLevel(std::ostream &stream, LogLevel p) {
    switch (p) {
    case LogLevel::FATAL:
        stream << "[FATAL]";
        break;
    case LogLevel::ERROR:
        stream << "[ERROR]";
        break;
    case LogLevel::WARN:
        stream << "[WARN ]";
        break;
    case LogLevel::INFO:
        stream << "[INFO ]";
        break;
    case LogLevel::DEBUG:
        stream << "[DEBUG]";
        break;
    case LogLevel::TRACE:
        stream << "[TRACE]";
        break;
    default:
        break;
    }
}

bool isLogLevelEnabled(LogLevel p) noexcept {
    return p >= NetworKit::GlobalState::getLogLevel();
}

void printTime(std::ostream &stream,
               const std::chrono::time_point<std::chrono::system_clock> &timePoint) {
    stream << "[" << timePoint.time_since_epoch().count() << "]";
}

void printLocation(std::ostream &stream, const Location &loc) {
    stream << "[" << loc.file << ", " << loc.line << ": " << loc.function << "]";
}

std::tuple<std::string, std::string> getTerminalFormat(LogLevel p) {
    switch (p) {
    case LogLevel::FATAL:
        return std::make_tuple("\033[1;31m", "\033[0m");
    case LogLevel::ERROR:
        return std::make_tuple("\033[31m", "\033[0m");
    case LogLevel::WARN:
        return std::make_tuple("\033[33m", "\033[0m");
    case LogLevel::INFO:
    case LogLevel::DEBUG:
    case LogLevel::TRACE:
        return std::make_tuple("", "");
    default:
        // this only exists to silence a warning:
        // TODO: consider replacing it with __builtin_unreachable();
        throw std::logic_error{"invalid loglevel. This should NEVER happen"};
    }
}

static void logToTerminal(const Location &loc, LogLevel p,
                          const std::chrono::time_point<std::chrono::system_clock> &timePoint,
                          std::string_view msg) {
    std::stringstream stream;

    if (NetworKit::GlobalState::getPrintTime()) {
        printTime(stream, timePoint);
    }

    std::string termFormatOpen, termFormatClose;
    std::tie(termFormatOpen, termFormatClose) = getTerminalFormat(p);

    stream << termFormatOpen;
    printLogLevel(stream, p);
    stream << termFormatClose;

    if (NetworKit::GlobalState::getPrintLocation()) {
        printLocation(stream, loc);
    }

    stream << ": ";

    stream << termFormatOpen;
    stream << msg;
    stream << termFormatClose;

    stream.put('\n');

    static std::mutex cerr_mutex;
    {
        std::lock_guard<std::mutex> guard{cerr_mutex};
        std::cerr << stream.str();
    }
}

static void logToFile(const Location &loc, LogLevel p,
                      const std::chrono::time_point<std::chrono::system_clock> &timePoint,
                      std::string_view msg) {
    if (!NetworKit::GlobalState::getLogFileIsOpen()) {
        return;
    }
    std::stringstream stream;
    printTime(stream, timePoint);
    stream << ' ';
    printLogLevel(stream, p);

    if (NetworKit::GlobalState::getPrintLocation()) {
        stream << ' ';
        printLocation(stream, loc);
    }

    stream << ": " << msg << '\n';
    {
        std::lock_guard<std::mutex> guard{NetworKit::GlobalState::getLogFileMutex()};
        if (!NetworKit::GlobalState::getLogFileIsOpen()) {
            return;
        }
        NetworKit::GlobalState::getLogFile() << stream.str() << std::flush;
    }
}

namespace Impl {

void log(const Location &loc, LogLevel p, std::string_view msg) {
    auto time = std::chrono::system_clock::now();

    logToTerminal(loc, p, time, msg);
    logToFile(loc, p, time, msg);
}

} // namespace Impl

} // namespace Log
} // namespace Aux
