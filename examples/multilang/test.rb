require "msgpack"

message = MessagePack.unpack(STDIN.read)

message["count"].times do |i|
  puts i.to_msgpack
end
