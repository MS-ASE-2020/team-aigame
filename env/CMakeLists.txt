find_package(Protobuf REQUIRED)

# add the executable
add_executable(env engine.cpp deck.cpp localPlayer.cpp message.pb.cc main.cpp stringify.cpp)
target_link_libraries(env ${Protobuf_LIBRARIES})