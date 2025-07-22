 Hybrid ML-OS Thread Scheduler


## Key Features ✨
- **ML-Powered Decisions**: Random Forest classifier predicts optimal thread execution
- **Real-Time Monitoring**: Tracks CPU/memory usage with `psutil`
- **Cross-Platform**: Python GUI + C++ backend communication via sockets
- **Interactive Dashboard**: Tkinter GUI with theme switching and execution logs

## How It Works 🔧
1. **GUI** accepts thread parameters (CPU, Priority, Deadline, etc.)
2. **Python ML Model** evaluates if thread should run
3. **C++ Scheduler** executes approved threads safely
4. **Real-Time Updates** shown in GUI

Execution:

# Terminal 1: Start ML server
python train_model.py
python ml_predictor.py

# Terminal 2: Launch GUI
python gui.py

# Terminal 3: Run C++ scheduler
g++ main.cpp -o scheduler -pthread -std=c++17
./scheduler

Tech Stack 🛠️
Component	        Technologies Used
Machine Learning	scikit-learn, joblib
Backend	          C++17 (Multithreading, Sockets)
Frontend	        Python Tkinter
Communication	    TCP/UDP Sockets

