import sys
import heapq as hq

class Process:
    id = 1
    def __init__(self, arrive, duration):
        self.id = Process.id
        Process.id += 1
        self.arrive = arrive
        self.duration = duration
        self.remaining = duration
        self.start = None
        self.end = None
        self.processed = False
        self.wait = None
        self.response = None
        self.turnaround = None

    def __lt__(self, other):
        if self.remaining < other.remaining:
            return True
        return False
    
    def __str__(self) -> str:
        return f"{self.arrive} {self.duration}"
    
    def __repr__(self) -> str:
        return f"P{self.id}"
    
    def analyze(self):
        self.response = self.start - self.arrive
        self.turnaround = self.end - self.arrive
        self.wait = self.turnaround - self.duration


def parseFile():
    arrivals = []
    bursts = []
    processes = []
    file = sys.stdin
    for line in file:
        line = line.strip()
        line_split = line.split()
        arrivals.append(int(line_split[0]))
        bursts.append(int(line_split[1]))
        p = Process(int(line_split[0]), int(line_split[1]))
        processes.append(p)
    return (arrivals, bursts, processes)

def FCFS(arrivals, bursts):
    length = len(arrivals)
    prev_end = -1
    waits = 0
    turnarounds = 0
    responses = 0

    for i in range(length):
        arrive = int(arrivals[i])
        burst = int(bursts[i])
        start = prev_end if arrive < prev_end else arrive
        end = start + burst
        wait = start - arrive
        turnaround = end - arrive
        resp = wait
        prev_end = end

        waits += wait
        turnarounds += turnaround
        responses += resp

    print("First Come, First Served")
    print(f"Avg. Resp: {responses / length}, Avg TA: {turnarounds/length}, Avg Wait: {waits/length}")
    print()

def SJF(arrivals, bursts):
    size = len(arrivals)
    waits = 0
    turnarounds = 0
    responses = 0
    processed = 0

    ctime = arrivals[0]
    ready = []


    hq.heappush(ready, [bursts[0], arrivals[0], 1])
    arrivals[0] = -1
    bursts[0] = -1

    while (processed < size):
        while(ready):
            arrive = ready[0][1]
            burst = ready[0][0]
            start = ctime
            end = start + burst

            turnaround = end - arrive
            wait = turnaround - burst
            resp = start - arrive

            waits += wait
            turnarounds += turnaround
            responses += resp

            ctime += ready[0][0]
            processed += 1


            hq.heappop(ready)
            
            for i in range(size):
                if (arrivals[i] <= ctime and arrivals[i] != -1):
                    hq.heappush(ready, [bursts[i], arrivals[i]])

                    arrivals[i] = -1
                    bursts[i] = -1
        for i in range(size):
            if (arrivals[i] != -1):
                ctime = arrivals[i]
                hq.heappush(ready, [bursts[i], arrivals[i]])
                arrivals[i] = -1
                bursts[i] = -1
                break

    print("Shortest Job First")
    print("Avg Resp:", responses/size,end=", ")
    print("Avg TA:", turnarounds/size,end=", ")
    print("Avg Wait:", waits/size)
    print()

def SRTF(processes):
    size = len(processes)
    waits = 0
    turnarounds = 0
    responses = 0
    processed = 0

    ctime = processes[0].arrive
    ready = []


    hq.heappush(ready, processes[0])

    while (processed < size):
        while(ready):
            p = ready[0]
            arrive = p.arrive
            burst = p.remaining
            start = ctime
            if not p.start: p.start = ctime
            potential_end = start + burst
            
            next_process = None
            for i in range(p.id, size):
                if not processes[i] in ready and processes[i].arrive < potential_end and not processes[i].processed:
                    next_process = processes[i]
                    break
                elif processes[i].arrive > potential_end:
                    break
            
            if not next_process:
                p.end = potential_end
                p.remaining = 0
                p.processed = True
                ctime += burst
                processed += 1
            else:
                elapsed = next_process.arrive - start
                p.remaining -= elapsed
                ctime = next_process.arrive


            hq.heappop(ready)
            
            for p in processes:
                if (not p in ready and p.arrive <= ctime and not p.processed):
                    hq.heappush(ready, p)
        for p in processes:
            if (not p.processed):
                ctime = p.arrive
                hq.heappush(ready, p)
                break

    for p in processes:
        p.analyze()

        responses += p.response
        turnarounds += p.turnaround
        waits += p.wait


    print("Shortest Remaining Time First")
    print("Avg Resp:", responses/size,end=", ")
    print("Avg TA:", turnarounds/size,end=", ")
    print("Avg Wait:", waits/size)
    print()

def RR(processes):
    # If the time quantum is not passed in use 100 by default
    if len(sys.argv) <= 1:
        quantum = 100
    if len(sys.argv) > 1:
        quantum = int(sys.argv[1])
    print("Round Robin with Time Quantum of {}".format(quantum))

    size = len(processes)

    # ctime will keep of the current time, it starts when the first process arrives
    ctime = processes[0].arrive
    
    # I'm going to use a ready queue to keep track of what processes are ready to run,
    # and the order for them to run in.
    ready = []
    # Keep track of what processes have been completed
    completed = []

    p = processes[0]
    ready.append(p)
    # I'm going use the input processes list to keep track of what processes
    # haven't "arrived yet". So when a process arrives I will remove it from that list.
    # They will be kept in the ready or the completed lists
    processes.remove(p)

    while (True):
        
        # Continue running while there is a process in the ready array.
        # If there isn't one in the ready array we need to see if there are any more "coming".
        while(ready):
            p = ready.pop(0)
            start = ctime
            # If this process that is running doesn't have a start time, set the start time
            if not p.start: p.start = ctime


            if p.remaining - quantum <= 0:
                # If the process is completed while the time quantum is running
                # Finish the process and remove it from ready
                ctime += p.remaining
                p.remaining = 0
                p.end = ctime
                p.processed = True
                completed.append(p)
            elif p.remaining - quantum > 0:
                # There is time remaining when the time quatum cuts it off.
                ctime += quantum
                p.remaining -= quantum


            for proc in processes:
                # I need to see if there are any process that have arrived while the current process 
                # has been running.
                if proc.arrive <= ctime:
                    processes.remove(proc)
                    ready.append(proc)
                elif p.arrive > ctime:
                    # since they are list in order of arrival time,
                    # as soon as I find a process that arrives after the current time
                    # I can stop checking.
                    break

            if not p.processed: ready.append(p) 
            # Add the process that just finished to the end of the ready queue.
            """
            #####
            THIS MAY BE WHERE I AM GOING WRONG! Does it current process go in front of,
            or behind the new processes?
            """
        if len(processes) > 0: # Check to see if more processes are "coming"
            p = processes[0]
            processes.remove(p)
            ready.append(p)
            ctime = p.arrive
        else:
            break
        
    
    waits = 0
    responses = 0
    turnarounds = 0
    for p in completed:
        # Compute the statistics for individual processes, and for the averages.
        p.turnaround = p.end - p.arrive
        p.response = p.start - p.arrive
        p.wait = p.turnaround - p.duration
        waits += p.wait
        responses += p.response
        turnarounds += p.turnaround
    


    print("Avg resp: {:.2f}".format(responses/size), end="\t\t")
    print("Avg TA: {:.2f}".format(turnarounds/size), end="\t\t")
    print("Avg wait: {:.2f}".format(waits/size), end="\t\t")
    print()

    



def main():
    arrivals, bursts, processes = parseFile()
    FCFS(arrivals.copy(), bursts.copy())
    SJF(arrivals.copy(), bursts.copy())
    SRTF(processes)
    RR(processes)
    

main()