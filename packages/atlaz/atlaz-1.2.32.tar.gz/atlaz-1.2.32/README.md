# atlaz Documentation

## Installation

You can install `atlaz` directly from PyPI:

```bash
pip install atlaz
```

---

## Atlaz Code Quickstart
Run this in your terminal in the root directory of your project
```Terminal
python3 -m venv
source venv/bin/activate
pip3 install atlaz
atlaz-prepare
```
and then create another terminal, also in the root directory of your project
```Terminal
python3 -m venv
source venv/bin/activate
pip3 install atlaz
atlaz-code
```



## Atlaz Knowledge Graph Quickstart
Here’s a minimal example to get started quickly:

```example_script.py
from atlaz.headquarter.client import AtlazClient
from atlaz.graph.examples import attention_is_all_you_need

# Initialize client (You need to have a gemini API key)
client = AtlazClient(api_key=GEMINI_API_KEY)
# Build Knowledge Graph
response = client.build_graph(source_text=attention_is_all_you_need)
# Render Graphviz Graph
visualize(response['graph'], 'attention_graph')
```
You can also add a customization argument to describe what entities or relationships to focus on, as well as a graph argument to expand on an existing graph.

---


## Core Concepts

### Knowledge Graph Structure

A knowledge graph in `atlaz` consists of nodes, edges, and categories. Each node represents an entity or concept. Edges define relationships between these entities, and categories group nodes into meaningful subsets. There is much more to come here with grouping nodes, especially with regards to collectively exhaustive subclasses of entities.

Here is the pydantic schema of the Graph Object:
```pydantic_schema.py
from typing import List, Optional
from pydantic import BaseModel, Extra, Field # type: ignore

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier of the node.")
    label: str = Field(..., description="Human-readable label of the node.")
    color: str = Field(..., description="Color used to represent the node.")
    shape: str = Field(..., description="Shape used to represent the node, e.g., 'ellipse', 'box', etc.")

class Edge(BaseModel):
    source: str = Field(..., description="ID of the source node.")
    target: str = Field(..., description="ID of the target node.")
    type: Optional[str] = Field(None, description="Type of relationship, e.g., 'subtype' or 'other'.")
    color: str = Field(..., description="Color used to represent the edge.")
    arrowhead: str = Field(..., description="Shape of the arrowhead, e.g., 'normal', 'diamond'.")
    label: Optional[str] = Field(None, description="Optional label for the edge relationship.")

class Category(BaseModel):
    name: str = Field(..., description="Name of the category.")
    color: str = Field(..., description="Color used to represent the category.")

class Graph(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the graph.")
    edges: List[Edge] = Field(..., description="List of edges in the graph.")
    categories: List[Category] = Field(..., description="List of categories associated with the graph.")
```



Here is how an example graph object can look.

```example_json.py
{
        "nodes": [
            {
                "id": "1",
                "label": "Transformer",
                "color": "lightgreen",
                "shape": "box",
                "info": "A model architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
            },
            {
                "id": "2",
                "label": "Recurrent Neural Network (RNN)",
                "color": "lightgreen",
                "shape": "box",
                "info": "A type of neural network where connections between nodes form a directed graph along a temporal sequence."
            },
            {
                "id": "3",
                "label": "Convolutional Neural Network (CNN)",
                "color": "lightgreen",
                "shape": "box",
                "info": "A class of deep neural networks, most commonly applied to analyzing visual imagery."
            },
            {
                "id": "4",
                "label": "Encoder-Decoder Architecture",
                "color": "lightgreen",
                "shape": "box",
                "info": "A neural network design pattern for sequence-to-sequence tasks, consisting of an encoder to process the input and a decoder to generate the output."
            },
            {
                "id": "20",
                "label": "Neural Network Model",
                "color": "lightgreen",
                "shape": "box",
                "info": "A computational model inspired by the way biological neural networks in the human brain process information."
            },
            {
                "id": "5",
                "label": "Self-Attention",
                "color": "lightblue",
                "shape": "box",
                "info": "An attention mechanism relating different positions of a single sequence to compute a representation of the sequence."
            },
            {
                "id": "6",
                "label": "Scaled Dot-Product Attention",
                "color": "lightblue",
                "shape": "box",
                "info": "An attention mechanism where the dot products of the query with all keys are computed, divided by the square root of the dimension of the keys, and a softmax function is applied to obtain the weights on the values."
            },
            {
                "id": "7",
                "label": "Multi-Head Attention",
                "color": "lightblue",
                "shape": "box",
                "info": "An attention mechanism that allows the model to jointly attend to information from different representation subspaces at different positions."
            },
            {
                "id": "21",
                "label": "Attention Mechanism",
                "color": "lightblue",
                "shape": "box",
                "info": "A process that allows a model to focus on specific parts of the input sequence when producing an output."
            },
            {
                "id": "8",
                "label": "Machine Translation",
                "color": "lightyellow",
                "shape": "box",
                "info": "The task of automatically converting text from one language to another."
            },
            {
                "id": "9",
                "label": "English Constituency Parsing",
                "color": "lightyellow",
                "shape": "box",
                "info": "The task of analyzing the syntactic structure of a sentence according to a constituency-based grammar."
            },
            {
                "id": "22",
                "label": "Task",
                "color": "lightyellow",
                "shape": "box",
                "info": "A specific function or activity that a model is designed to perform."
            },
            {
                "id": "10",
                "label": "BLEU Score",
                "color": "orange",
                "shape": "box",
                "info": "A metric for evaluating a generated sentence to a reference sentence, used in machine translation."
            },
            {
                "id": "11",
                "label": "Dropout",
                "color": "pink",
                "shape": "box",
                "info": "A regularization technique for reducing overfitting in neural networks by preventing complex co-adaptations on training data."
            },
            {
                "id": "12",
                "label": "Label Smoothing",
                "color": "pink",
                "shape": "box",
                "info": "A technique used during training to make the model less confident, improving accuracy and BLEU score."
            },
            {
                "id": "23",
                "label": "Training Technique",
                "color": "pink",
                "shape": "box",
                "info": "A method or strategy used to improve the performance of a model during training."
            },
            {
                "id": "24",
                "label": "Concept",
                "color": "lime",
                "shape": "box",
                "info": "A general idea or understanding of something."
            }
        ],
        "edges": [
            {
                "source": "20",
                "target": "1",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "The Transformer is a type of neural network model."
            },
            {
                "source": "20",
                "target": "2",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Recurrent Neural Networks are a type of neural network model."
            },
            {
                "source": "20",
                "target": "3",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Convolutional Neural Networks are a type of neural network model."
            },
            {
                "source": "20",
                "target": "4",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Encoder-Decoder Architecture is a type of neural network model."
            },
            {
                "source": "21",
                "target": "5",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Self-Attention is a type of attention mechanism."
            },
            {
                "source": "21",
                "target": "6",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Scaled Dot-Product Attention is a type of attention mechanism."
            },
            {
                "source": "21",
                "target": "7",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Multi-Head Attention is a type of attention mechanism."
            },
            {
                "source": "22",
                "target": "8",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Machine Translation is a type of task."
            },
            {
                "source": "22",
                "target": "9",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "English Constituency Parsing is a type of task."
            },
            {
                "source": "23",
                "target": "11",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Dropout is a type of training technique."
            },
            {
                "source": "23",
                "target": "12",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Label Smoothing is a type of training technique."
            },
            {
                "source": "24",
                "target": "21",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Attention Mechanism is a type of concept."
            },
            {
                "source": "24",
                "target": "20",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Neural Network Model is a type of concept."
            },
            {
                "source": "24",
                "target": "22",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Task is a type of concept."
            },
            {
                "source": "24",
                "target": "23",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Training Technique is a type of concept."
            },
            {
                "source": "24",
                "target": "10",
                "type": "subtype",
                "color": "black",
                "arrowhead": "normal",
                "label": "type of",
                "info": "Metric is a type of concept."
            },
            {
                "source": "1",
                "target": "5",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "uses",
                "info": "The Transformer uses self-attention to compute representations of its input and output."
            },
            {
                "source": "1",
                "target": "10",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "achieves",
                "info": "The Transformer achieves a BLEU score of 28.4 on the WMT 2014 English-to-German translation task."
            },
            {
                "source": "1",
                "target": "10",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "achieves",
                "info": "The Transformer achieves a BLEU score of 41.8 on the WMT 2014 English-to-French translation task."
            },
            {
                "source": "1",
                "target": "8",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "applied_to",
                "info": "Machine Translation is a task where the Transformer has been applied successfully."
            },
            {
                "source": "1",
                "target": "9",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "applied_to",
                "info": "English Constituency Parsing is a task where the Transformer has been applied successfully."
            },
            {
                "source": "11",
                "target": "1",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "used_in",
                "info": "Dropout is used in the training of the Transformer to prevent overfitting."
            },
            {
                "source": "12",
                "target": "1",
                "type": "dependency",
                "color": "black",
                "arrowhead": "diamond",
                "label": "used_in",
                "info": "Label Smoothing is used in the training of the Transformer to improve accuracy and BLEU score."
            }
        ],
        "categories": [
            {
                "name": "Neural Network Models",
                "color": "lightgreen"
            },
            {
                "name": "Attention Mechanisms",
                "color": "lightblue"
            },
            {
                "name": "Tasks",
                "color": "lightyellow"
            },
            {
                "name": "Metrics",
                "color": "orange"
            },
            {
                "name": "Training Techniques",
                "color": "pink"
            },
            {
                "name": "Concepts",
                "color": "lime"
            }
        ]
    }
```

---

### Visualization Functions

The `visualize` function takes a graph dictionary and filename and uses graphviz to create a graph based on it. The format of the data is according to the pydantic schema above.

```
from atlaz.graph.examples import attention_is_all_you_need_object
from atlaz.graph.graph import visualize
visualize(attention_is_all_you_need_object, 'graph_name')
```

---

## License

`atlaz` is released under the [MIT License].

*This documentation was last updated on 19/12-2024. For the latest updates and additional tutorials, visit our [official website](atlaz.ai).*