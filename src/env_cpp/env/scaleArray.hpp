#pragma once

#include <cstddef>
#include "exception.h"

#include <cstdio>

namespace AlgoLib::DataStructure{
    template<typename T>
    class ScaleArray{
        protected:
        T* m_mem;
        const static size_t m_default_init_cap = 64;
        size_t m_size;
        size_t m_capacity;

        void allocMem(size_t elementCount){
            m_mem = reinterpret_cast<T*>(new char[sizeof(T) * elementCount]);
        }

        void deallocMem(){
            delete[] (char *)m_mem;
        }

        bool indexInBound(size_t index){
            return index < m_size;
        }

        void relocate(T* location, size_t capacity);

        void setCapacity(size_t capacity);

        ScaleArray(const ScaleArray& other, size_t capacity): m_size(other.m_size), m_capacity(capacity){
            if(m_size > m_capacity){
                // not allowed to shrink below m_size
                throw AlgoLib::Exception(AlgoLib::Exception::UNEXPECTED);
            }

            allocMem(m_capacity);
            for(int i = 0; i < m_size; ++i){
                new(&m_mem[i]) T(other.m_mem[i]);
            }
        }
        
        public:
        ScaleArray(): m_size(0), m_capacity(m_default_init_cap){
            allocMem(m_capacity);
        }

        ScaleArray(size_t capacity): m_size(0), m_capacity(capacity){
            allocMem(m_capacity);
        }

        virtual ~ScaleArray(){
            if(m_mem != nullptr){
                clear();
                deallocMem();
            }
        }

        ScaleArray(const ScaleArray& other): m_size(other.m_size), m_capacity(other.m_capacity){
            allocMem(m_capacity);
            for(int i = 0; i < m_size; ++i){
                new(&m_mem[i]) T(other.m_mem[i]);
            }
        }

        ScaleArray(ScaleArray&& other): m_size(other.m_size), m_capacity(other.m_capacity){
            m_mem = other.m_mem;
            other.m_mem = nullptr;
        }

        T* data(){
            return m_mem;
        }

        void push_back(const T& element);
        void push_back(T&& element);
        void pop_back();

        const T& operator [] (size_t index) const;
        T& operator[] (size_t index);
        ScaleArray& operator = (const ScaleArray& other);
        ScaleArray& operator = (ScaleArray&& other);
        ScaleArray& operator = (ScaleArray other) = delete;
        void swap(ScaleArray& other);

        const T& front() const;
        T& front();
        const T& back() const;
        T& back();

        inline bool empty() const;
        void clear();

        inline size_t size() const;
        inline size_t capacity() const;

        void resize(size_t size);
        void reserve(size_t capacity);
        void shrink_to_fit();
    };

    template<typename T>
    size_t ScaleArray<T>::size() const {
        return m_size;
    }

    template<typename T>
    size_t ScaleArray<T>::capacity() const {
        return m_capacity;
    }

    template<typename T>
    bool ScaleArray<T>::empty() const {
        return m_size == 0;
    }

    template<typename T>
    void ScaleArray<T>::clear(){
        if(m_mem == nullptr){
            return;
        }

        for(int i = 0; i < m_size; ++i){
            m_mem[i].~T();
        }
        m_size = 0;
    }

    template<typename T>
    const T& ScaleArray<T>::front() const {
        if(m_size == 0){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[0];
    }

    template<typename T>
    T& ScaleArray<T>::front(){
        if(m_size == 0){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[0];
    }

    template<typename T>
    const T& ScaleArray<T>::back() const {
        if(m_size == 0){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[m_size - 1];
    }

    template<typename T>
    T& ScaleArray<T>::back(){
        if(m_size == 0){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[m_size - 1];
    }

    template<typename T>
    const T& ScaleArray<T>::operator [] (size_t index) const {
        if(!indexInBound(index)){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[index];
    }

    template<typename T>
    T& ScaleArray<T>::operator [] (size_t index){
        if(!indexInBound(index)){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        return m_mem[index];
    }

    template<typename T>
    ScaleArray<T>& ScaleArray<T>::operator = (const ScaleArray<T>& other){
        this->clear();
        m_size = other.m_size;

        if(m_capacity < m_size){
            // Must resize
            m_capacity = other.m_capacity;
            deallocMem();
            allocMem(m_capacity);
        }

        for(int i = 0; i < m_size; ++i){
            new (&m_mem[i]) T(other.m_mem[i]);
        }

        return *this;
    }

    template<typename T>
    ScaleArray<T>& ScaleArray<T>::operator = (ScaleArray&& other){
        this->clear();
        m_size = other.m_size;
        m_capacity = other.m_capacity;
        m_mem = other.m_mem;
        other.m_mem = nullptr;

        return *this;
    }

    template<typename T>
    void ScaleArray<T>::relocate(T* location, size_t capacity){
        ScaleArray<T> temp(*this, capacity);
        swap(temp);
    }

    template<typename T>
    void ScaleArray<T>::setCapacity(size_t capacity){
        if(m_capacity == capacity){
            return;
        }

        if(m_size > capacity){
            // not allowed to shrink below m_size
            throw AlgoLib::Exception(AlgoLib::Exception::UNEXPECTED);
        }

        T* memory = reinterpret_cast<T*>(new char[sizeof(T) * capacity]);
        relocate(memory, capacity);
    }

    template<typename T>
    void ScaleArray<T>::push_back(const T& element){
        size_t newSize = m_size + 1;
        if(newSize > m_capacity){
            if(m_capacity == 0){
                setCapacity(1);
            }
            else{
                setCapacity(m_capacity << 1);
            }
        }

        new (&m_mem[m_size]) T(element);
        m_size = newSize;
    }

    template<typename T>
    void ScaleArray<T>::push_back(T&& element){
        size_t newSize = m_size + 1;
        if(newSize > m_capacity){
            if(m_capacity == 0){
                setCapacity(1);
            }
            else{
                setCapacity(m_capacity << 1);
            }
        }

        new (&m_mem[m_size]) T(element);
        m_size = newSize;
    }

    template<typename T>
    void ScaleArray<T>::pop_back(){
        if(m_size == 0){
            throw AlgoLib::Exception(AlgoLib::Exception::INDEX_OOB);
        }

        m_mem[m_size - 1].~T();
        --m_size;
    }

    template<typename T>
    void ScaleArray<T>::resize(size_t size){
        if(size <= m_size){
            for(int i = size; i < m_size; ++i){
                m_mem[i].~T();
            }
        }
        else{
            T temp;
            for(int i = m_size; i < size; ++i){
                push_back(temp);
            }
        }

        m_size = size;
    }

    template<typename T>
    void ScaleArray<T>::reserve(size_t capacity){
        if(capacity > m_capacity){
            setCapacity(capacity);
        }
    }

    template<typename T>
    void ScaleArray<T>::shrink_to_fit(){
        setCapacity(m_size);
    }

    template<typename T>
    void ScaleArray<T>::swap(ScaleArray<T>& other){
        T* tmpPtr = m_mem;
        m_mem = other.m_mem;
        other.m_mem = tmpPtr;

        size_t tmpSize = m_size;
        m_size = other.m_size;
        other.m_size = tmpSize;

        tmpSize = m_capacity;
        m_capacity = other.m_capacity;
        other.m_capacity = tmpSize;
    }

} // AlgoLib::DataStructure
