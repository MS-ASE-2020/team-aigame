#pragma once

#include <string>

namespace AlgoLib{

    class Exception{
        private:
        int m_errcode;
        std::string m_reason;

        public:
        Exception(int code): m_errcode(code), m_reason(){}
        Exception(int code, std::string reason): m_errcode(code), m_reason(reason){}
        ~Exception(){}

        int code() const {
            return m_errcode;
        }

        const static int OK = 0;
        const static int SIZE_TOOLARGE = OK + 1;
        const static int ALLOC_FAILURE = SIZE_TOOLARGE + 1;
        const static int ARG_ILL_FORMAT = ALLOC_FAILURE + 1;
        const static int INDEX_OOB = ARG_ILL_FORMAT + 1;
        const static int UNEXPECTED = INDEX_OOB + 1;
        const static int MATRIX_SIZE_ERROR = UNEXPECTED + 1;
    };

}