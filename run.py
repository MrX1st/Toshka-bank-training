import sys
import heapq

ENERGY = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
ROOMS = ['A', 'B', 'C', 'D']
ROOM_POS = [2, 4, 6, 8]
HALLWAY_POS = [0, 1, 3, 5, 7, 9, 10]

def parse_input(lines):
    depth = len(lines) - 3
    corridor = [0]*11
    rooms = [[0]*depth for _ in range(4)]
    mapping = {'.':0,'A':1,'B':2,'C':3,'D':4}
    for d in range(depth):
        row = lines[2+d]
        for r,pos in enumerate([3,5,7,9]):
            rooms[r][d] = mapping[row[pos]]
    return corridor, rooms

def state_to_bytes(corridor, rooms):
    b = corridor[:]
    for r in rooms:
        b.extend(r)
    return bytes(b)

def unpack_state(state_bytes, depth):
    corridor = list(state_bytes[:11])
    rooms = []
    for r in range(4):
        rooms.append(list(state_bytes[11+r*depth:11+(r+1)*depth]))
    return corridor, rooms

def possible_moves(corridor, rooms, depth):
    moves = []

    # Hallway -> Room (priority 0)
    for hp in HALLWAY_POS:
        amph = corridor[hp]
        if amph==0:
            continue
        target_room = amph-1
        room_slots = rooms[target_room]
        if any(x != 0 and x != amph for x in room_slots):
            continue
        start_pos = hp
        end_pos = ROOM_POS[target_room]
        step = 1 if end_pos>start_pos else -1
        if all(corridor[p]==0 for p in range(start_pos+step,end_pos+step,step)):
            # move to deepest empty slot
            for d in reversed(range(depth)):
                if room_slots[d]==0:
                    break
            new_corr = corridor[:]
            new_rooms = [r[:] for r in rooms]
            new_corr[hp] = 0
            new_rooms[target_room][d] = amph
            cost = (abs(end_pos-start_pos)+d+1)*ENERGY[ROOMS[amph-1]]
            moves.append((state_to_bytes(new_corr,new_rooms), cost))

    # Room -> Hallway (priority 1)
    for r, room in enumerate(rooms):
        for d, val in enumerate(room):
            if val==0:
                continue
            amph = val
            target_room = amph-1
            if r==target_room and all(x==amph for x in room[d:]):
                continue
            start_pos = ROOM_POS[r]
            for hp in HALLWAY_POS:
                step = 1 if hp>start_pos else -1
                if all(corridor[p]==0 for p in range(start_pos+step,hp+step,step)):
                    new_corr = corridor[:]
                    new_rooms = [room[:] for room in rooms]
                    new_rooms[r][d]=0
                    new_corr[hp]=amph
                    cost = (abs(hp-start_pos)+d+1)*ENERGY[ROOMS[amph-1]]
                    moves.append((state_to_bytes(new_corr,new_rooms), cost))
            break
    return moves

def solve(lines):
    depth = len(lines)-3
    corridor, rooms = parse_input(lines)
    start = state_to_bytes(corridor, rooms)
    goal_rooms = [[i+1]*depth for i in range(4)]
    goal = state_to_bytes([0]*11, goal_rooms)

    heap = [(0, start)]
    seen = {start:0}

    while heap:
        g, state = heapq.heappop(heap)
        if state==goal:
            return g
        corridor, rooms = unpack_state(state, depth)
        for new_state, cost in possible_moves(corridor, rooms, depth):
            ng = g + cost
            if new_state not in seen or ng<seen[new_state]:
                seen[new_state] = ng
                heapq.heappush(heap, (ng, new_state))
    return -1

def main():
    lines = [line.rstrip('\n') for line in sys.stdin]
    print(solve(lines))

if __name__=="__main__":
    main()
