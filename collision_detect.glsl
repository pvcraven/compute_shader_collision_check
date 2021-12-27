#version 430

// Set up our compute groups
layout(local_size_x=256, local_size_y=1) in;

uniform vec2 check_pos;
uniform vec2 check_size;

// Structure of the ball data
struct SpritePosition
{
    vec2 position;
};

// Structure of the ball data
struct SpriteSize
{
    vec2 size;
};

// Input buffer
layout(std430, binding=0) buffer sprites_pos_in
{
    SpritePosition sprite_positions[];
} InPos;

// Input buffer
layout(std430, binding=1) buffer sprites_size_in
{
    SpriteSize sprite_sizes[];
} InSize;


// Output buffer
layout(std430, binding=2) buffer collision_out
{
    int collision[];
} Out;

void main()
{
    int curSpriteIndex = int(gl_GlobalInvocationID);
    SpritePosition in_sprite_pos = InPos.sprite_positions[curSpriteIndex];
    SpriteSize in_sprite_size = InSize.sprite_sizes[curSpriteIndex];
//    float dist = distance(in_sprite_pos.position, check_pos);
    float xdiff = abs(in_sprite_pos.position.x - check_pos.x);
    float ydiff = abs(in_sprite_pos.position.y - check_pos.y);
    float maxdiff = max(xdiff, ydiff);

    // How far away can they be? 1/2 the dimension of the longest width or height, times square root of 2
    float max1 = max(check_size.x, check_size.y);
    float max2 = max(in_sprite_size.size.x, in_sprite_size.size.y);
    float max3 = max(max1, max2) * .72;
    int result = 111;
    if (maxdiff < max3)
        result = 222;

    Out.collision[curSpriteIndex] = result;
}