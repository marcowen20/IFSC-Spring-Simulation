import tkinter as tk
import graphics
import numpy as np
import calculation as cal
import refs
import time
#matplotlib to tkinter
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

#Reusable slider template
class sliderControl:
    def __init__(self, master, name, variableName, range, resolution, default):
        self.variableName = variableName
        self.name = name
        self.minValue = range[0]
        self.maxValue = range[1]
        self.default = default
        self.resolution = resolution

        self.label = tk.Label(master,text=self.name)
        self.label.grid(sticky=tk.W)
        self.scale = tk.Scale(master, length=200, variable = self.variableName, from_=self.minValue, to=self.maxValue, orient=tk.HORIZONTAL, resolution=self.resolution)
        self.scale.set(self.default)
        self.scale.grid(sticky=tk.W)

#Reusable text entry template
class entryControl:
    def __init__(self, master, name, default):
        self.name = name
        self.default = default

        self.label = tk.Label(master, text=self.name)
        self.label.grid(sticky=tk.W)
        self.entry = tk.Entry(master, width=3)
        self.entry.grid(sticky=tk.W)

class MainApplication(tk.Tk):
    def UpdateControls(self):
        self.springConstant = self.springConstantControl.get()
        self.mass = self.massControl.get()
        self.initialDisplacement = self.initialDisplacementControl.get()
        self.velocity = self.velocityControl.get()
        self.timeStep = self.timeStepControl.get()
        self.movementMultiplier = self.movementMultiplierControl.get()
        self.springLength = self.springLengthControl.get()
        self.stopStep = self.stopStepControl.get()
        self.graphFrom = self.graphFromControl.get()
        self.graphTo = self.graphToControl.get()

        simulationCanvas1 = tk.Canvas(self.simulationFrame, width=250, height=800)
        simulationCanvas2 = tk.Canvas(self.simulationFrame, width=250, height=800)

        start = time.time()
        self.exactData = cal.GetExactValues(self.stopStep, self)
        end = time.time()
        exactComputeTime = end-start

        start = time.time()
        self.approximateData = cal.GetApproximateValues(self.stopStep, self, refs.ETSHM6)
        end = time.time()
        approximateComputeTime = end-start

        differences = [abs(self.exactData[i] - self.approximateData[i]) for i in range(0, self.stopStep)]
        self.globalErrorLabel.config(text="Global error: {}".format(str(round(max(differences), 10))))
        self.canvas1LabelTime.config(text="Numerical compute time: {}s".format(round(approximateComputeTime, 4)))
        self.canvas2LabelTime.config(text="Exact value compute time: {}s".format(round(exactComputeTime, 4)))
        self.CreateGraph()
        self.CreateSimulation(simulationCanvas1, simulationCanvas2)

    def ResetControls(self):
        self.springConstantControl.set(1)
        self.massControl.set(4)
        self.initialDisplacementControl.set(1)
        self.velocityControl.set(5)
        self.timeStepControl.set(0.2)
        self.movementMultiplierControl.set(1)
        self.springLengthControl.set(480)
        self.stopStepControl.set(1000)
        self.graphFromControl.set(0)
        self.graphToControl.set(25)

    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title("Spring Simulation")
        self.controlFrame = tk.Frame(self)
        self.controlFrame.grid(row=0, column=0, padx=10, pady=10, sticky="N", columnspan=1)

        #Data variables
        self.exactData = []
        self.approximateData = []

        #Control variables
        self.springConstantControl = tk.DoubleVar()
        self.massControl = tk.DoubleVar()
        self.initialDisplacementControl = tk.DoubleVar()
        self.velocityControl = tk.DoubleVar()
        self.timeStepControl = tk.DoubleVar()
        self.movementMultiplierControl = tk.DoubleVar()
        self.springLengthControl = tk.DoubleVar()
        self.graphFromControl = tk.IntVar()
        self.graphToControl = tk.IntVar()
        self.stopStepControl = tk.IntVar()


        self.simulationFrame = tk.Frame(self)
        self.simulationFrame.grid(row=0, column=1, padx=10, pady=10, columnspan=1)
        self.graphFrame = tk.Frame(self)
        self.graphFrame.grid(row=0, column=2, padx=10, pady=10, columnspan=1)

        # ***** Control Frame *****
        #Equation variables
        springConstantControl = sliderControl(self.controlFrame, "Spring Constant, k (N/m)", self.springConstantControl, [0, 50], 0.01, 1)
        massControl = sliderControl(self.controlFrame, "Mass, m (kg)", self.massControl, [0, 100], 0.1, 4)
        initialDisplacementControl = sliderControl(self.controlFrame, "Initial Displacement, y₀ (m)", self.initialDisplacementControl, [-10, 10], 0.01, 1)
        velocityControl = sliderControl(self.controlFrame, "Velocity, y₀' (m/s)", self.velocityControl, [0, 50], 0.1, 5)
        timeStepControl = sliderControl(self.controlFrame, "timeStep, h", self.timeStepControl, [0, 3], 0.01, 0.2)

        #Other variables
        movementMultiplierControl = sliderControl(self.controlFrame, "Movement Multiplier", self.movementMultiplierControl, [0, 10], 0.1, 1)
        springLengthControl = sliderControl(self.controlFrame, "Spring Length (px)", self.springLengthControl, [0, 1080], 0.1, 480)
        stopStepControl = sliderControl(self.controlFrame, "Stop Step", self.stopStepControl, [0, 10000], 10, 100)
        graphFromControl = sliderControl(self.controlFrame, "Graph from", self.graphFromControl, [0, 10000], 10, 100)
        graphToControl = sliderControl(self.controlFrame, "Graph to", self.graphToControl, [0,10000], 10, 0)

        #Buttons
        updateButton = tk.Button(self.controlFrame, text="Update", command=self.UpdateControls).grid(sticky=tk.W, pady=5)
        resetButton = tk.Button(self.controlFrame, text="Reset Controls", command=self.ResetControls).grid(sticky=tk.W, pady=5)
        exitButton = tk.Button(self.controlFrame, text="Exit", command=self.destroy).grid(sticky=tk.W, pady=5)

        self.globalErrorLabel = tk.Label(self.controlFrame, text="Global error: ")
        self.globalErrorLabel.grid(sticky=tk.W, pady=5)

        #Initial labels
        canvas1Label = tk.Label(self.simulationFrame, text="Numerical Method")
        self.canvas1LabelTime = tk.Label(self.controlFrame, text="Numerical compute time:")
        canvas1Label.grid(row=0, column=0)
        self.canvas1LabelTime.grid(sticky=tk.W,pady=5)
        canvas2Label = tk.Label(self.simulationFrame, text="Exact Value")
        self.canvas2LabelTime = tk.Label(self.controlFrame, text="Exact value compute time:")
        canvas2Label.grid(row=0, column=1)
        self.canvas2LabelTime.grid(sticky=tk.W,pady=5)

    def CreateGraph(self):
        # ***** Graph Frame *****
        #Clear frame before creating graph canvas
        for canvas in self.graphFrame.winfo_children():
            canvas.destroy()

        graph = Figure(dpi=100)
        subplot = graph.add_subplot(111)
        subplot.set_xlabel('Time (s)')
        subplot.set_ylabel('Displacement (m)')
        graphFrom = self.graphFrom
        graphTo = self.graphTo
        xAxis = [x * (self.timeStep) for x in range(graphFrom, graphTo)]

        subplot.plot(xAxis, self.exactData[graphFrom:graphTo], label="Exact values")
        subplot.plot(xAxis, self.approximateData[graphFrom:graphTo], label="Numerical method")
        subplot.legend(loc='upper left')
        canvas = FigureCanvasTkAgg(graph, master=self.graphFrame)
        canvas.draw()
        canvas.get_tk_widget().grid(sticky="EW")

    def CreateSimulation(self, canvas1, canvas2):
        # ***** Simulation Frame *****
        simulationCanvas1 = canvas1
        simulationCanvas2 = canvas2

        simulationCanvas1.grid(row=1, column=0)
        simulationCanvas2.grid(row=1, column=1)

        # ----- Simulations -----
        #Define the entities
        object1 = graphics.Object(50)
        spring1 = graphics.Spring(object1, (250/2, 10), 100, self.springLength, 20, 8)
        object2 = graphics.Object(50)
        spring2 = graphics.Spring(object2, (250/2, 10), 100, self.springLength, 20, 8)

        #Animate the entities
        for x in range(0, len(self.exactData)):
            object1.displacement = self.approximateData[x] * self.movementMultiplier # TODO: Use the equations here
            object2.displacement = self.exactData[x] * self.movementMultiplier # TODO: Use the equations here
            #absoluteError = abs(self.approximateData[x] - self.exactData[x])
            simulationCanvas1.delete("all")
            simulationCanvas2.delete("all")
            spring1.Update()
            spring1.Draw(simulationCanvas1)
            spring2.Update()
            spring2.Draw(simulationCanvas2)

            simulationCanvas1.update()
            simulationCanvas2.update()
            time.sleep(0.05)

app = MainApplication()
app.mainloop()