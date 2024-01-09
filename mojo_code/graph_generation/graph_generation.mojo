# Create Graph data structure

# The graph must be a directed graph
#  Each node should have a link to another node
#  and the value of each node should be the name of the file
# We should visualize the graph with graphviz



#  For the Graphs data structures we can use Networkx or  check how pytorch geometric saves graphs and imitate the format.



# Data Structure:
# Hetergenous Directed Graph:
#   List of Nodes adjacency
#   The value of each node will be:
#          -File Name, Function name, Function Text, Function Documentation,  In dependencies Clustering Value,
            #  Out depedencie clustering value, Search Depth in, Search Depth out, Heuristic Function, In what class it is in.



#  Functions to create:

# Create a function that search for all the functions in the repository. Functions and classes are the nodes in the graph.

# When a function as already been found. It will extract the function information. It will retrieve the functions that uses.
#  If it is inside a class, the documentation, and where this function is used.


# It will execute Depth First Search. For each function inside the current function. 

#  It will keep track of python projects

# 

#  When doing the search we should have a logger




# The idea is the following:
# The DependencyGraph struct will only save the data of the FunctionNodes and  the dependencies for each one.
#  It will not execute the linking between Nodes. The Executor will be a separate class to which we will reference
#  the DependencyGraph to which we are going to add the data. The Executor will have the methods for initializing
#  The FunctionNodes and adding them to the Nodes in the DependencyGraph. Will also set the  Dependencies in the Hashmaps.
# We also going to have the Logger that will have the functions Decorators for the Executer Functions


from hashmap import HashMapDict
from ahasher import ahash
from memory.unsafe import Pointer
from python import Python
from pathlib import Path
from python.object import PythonObject
from memory.anypointer import AnyPointer


struct NodePointer[T: Movable](CollectionElement):
    var node: AnyPointer[T]
    fn __init__(inout self, pointerNode: AnyPointer[T] ):
        self.node = pointerNode

    fn __moveinit__(inout self, owned existing: Self):
        self.node = existing.node
    fn __copyinit__(inout self, borrowed existing: Self):
        self.node = existing.node

    
@value
struct FunctionNode(CollectionElement):
    var filepath: String
    var functionName: String
    var classOwnership:String
    var SearchDepth: Int
    
    fn __init__(inout self, functionName: String, classOwnership: String, filepath: String):
        self.filepath = filepath
        self.functionName = functionName
        self.classOwnership = classOwnership
        self.SearchDepth = 0

    fn hash_name(self) -> String:
        return self.filepath + self.classOwnership + self.functionName

    fn getPointer(inout self) -> NodePointer[FunctionNode]:
        let pointer = AnyPointer[FunctionNode]().alloc(1)
        let nodeptr = NodePointer(pointer)
        return pointer



@register_passable("trivial")
struct DependencyType:
    var value: Int

    alias inDependency = DependencyType(0)
    alias outDependency = DependencyType(1)

    fn __eq__(self, other: Self) -> Bool:
        return other.value == self.value
        
    fn __init__(value: Int) -> Self:
        return Self { value: value }


struct DependencyGraph(Movable):
        """
        Class for managing

        Args:


        Description:
        """
    var NodeCollection: DynamicVector[FunctionNode]
    var in_dependencies:HashMapDict[NodePointer[FunctionNode],ahash]
    var out_dependencies:HashMapDict[NodePointer[FunctionNode],ahash]
    var InitialDirectory : String
    var number_of_executers: Int
    var QueueDirectories: DynamicVector[String]


    fn __init__(inout self, InitialDirectory:String):
        self.NodeCollection = DynamicVector[FunctionNode]()
        self.in_dependencies = HashMapDict[NodePointer[FunctionNode], ahash]()
        self.out_dependencies = HashMapDict[NodePointer[FunctionNode], ahash]()
        self.InitialDirectory = InitialDirectory
        self.number_of_executers = 1
        self.QueueDirectories = DynamicVector[String](20)

    fn __moveinit__(inout self, owned existing: Self):
        self.InitialDirectory = existing.InitialDirectory

    fn __copyinit__(inout self, existing: Self):
        self.InitialDirectory = existing.InitialDirectory

    fn search_files(inout self):
        """
        returns:

        Args:d

        Description: Run the executers  that log all the functionnodes
        """



        # exec.add_node(self.InitialDirectory, GlobalNodeCollection = self.NodeCollection)

        # var a = self.NodeCollection[0]
        # print(a.functionName)


        


        pass
    fn calculate_relevant_nodes(inout self, DepType: DependencyType)-> DynamicVector[UInt8]:
        """
        Calculate the most relevant nodes veryfying who are the nodes with more 
        connections via relevance taking into account all the connections. Using 
        Markov Chains using the Google [Pagerank algorithm](https://en.wikipedia.org/wiki/PageRank).
        """
        return DynamicVector[UInt8]()
    fn BreathFirstSearchFiles(inout self, ) :
        """ Once the Dependencies storage has already being filled we will implement sa"""

        pass

    fn  search(inout self, initial_node: FunctionNode, Depth: Int):
        pass
    

struct Executors:
    var max_depth: Int
    var head_directory: Path
    var GlobalDependencyGraph : AnyPointer[DependencyGraph]
    var QueueDirectories: DynamicVector[String]

    fn __init__(inout self, head_directory: String, max_depth: Int, GlobalDependencyGraph: DependencyGraph):
        self.max_depth = max_depth
        self.head_directory = Path(head_directory)
        self.GlobalDependencyGraph = AnyPointer[DependencyGraph]().alloc(1)
        self.GlobalDependencyGraph.emplace_value(GlobalDependencyGraph)
        self.QueueDirectories = DynamicVector[String]()




    fn add_node(inout self, filepath: String):
        try:
            var file_text = Path(filepath).read_text()
            var e = FunctionNode(functionName = "c", classOwnership = "Yes",filepath= "d")
            var a = self.GlobalNodeCollection.take_value()
            a.push_back(e)





        except:
            print("Couln't read the Text of the file ")


    fn add_edges(self, inout node: FunctionNode,
                 inout in_dependencies: HashMapDict[NodePointer[FunctionNode], ahash]):
                 

                 in_dependencies.put(node.hash_name(), node.getPointer())





    fn search_files(inout self, directory: String, inout GlobalNodeCollection: DynamicVector[FunctionNode]) :
        # Read the File and start
        try:
            # Import the Python os library
            let os = Python.import_module("os")  
            var dir  = os.listdir(self.head_directory.path)
            var fullListDirectory: PythonObject = []
            var fullListFiles: PythonObject = []
            for entry in dir:
                let full_dir = os.path.join(self.head_directory.path, entry)
                if os.path.isfile(full_dir):
                    self.add_node()
                fullListDirectory.append(os.path.join(self.head_directory.path, entry))

            
                
            
       



            # let pathfile = pathlib.Path(path = self.head_directory)




        except:
            print("Error")

        
    fn add_edges(inout self, foundNode: FunctionNode):
        pass
    



struct NodeStorage:
    var e: Int

struct BaseStorage:
    var i: Int

struct GlobalStorage:
    var i : Int





struct Logger:
    var number_of_executers:Int

    
    fn __init__(inout self, number_of_executers: Int):
        self.number_of_executers = number_of_executers
    fn LoggerExecuter(self, executor_function: fn()-> None) :
        pass




fn data():
    pass


def DirectoryExploration():
    pass

def logInternalDependencies():
    pass

def getInDepedency():
    pass

def getOutDepdendency():
    pass

def LoggerExecuter():
    pass


