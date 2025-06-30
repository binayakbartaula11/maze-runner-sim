## Development Journey

This project began like so many do: just me, a blinking cursor, and a vague idea. From there, it became a long stretch of late nights, broken logic, and UI designs that made me question everything. There were plenty of false starts and moments where nothing seemed to work, no matter how hard I tried.

Honestly, this project had been sitting in my head for a few months. I started actively working on it around June, but the idea first came to me back in April, during the final exams of my fifth semester.

### Notebook Snapshot: Design Journal and Concept Sketch

<img src="/screenshot/log_snapshot_image.jpg" width="400" />

This page marks the early moments of the *Maze Generation and Solving Simulator* project, when it all existed as a rough idea, quickly jotted down in ink. It offers a glimpse into the initial thought process, where technical possibilities met creative exploration. These notes represent the transition from scattered concepts to a cohesive vision, much like the first sketch of a map guiding the journey ahead.

---

### **Contents of the Snapshot**

1. **Development Notes**
   This section outlines the maze generation algorithms chosen for the project: Recursive Backtracking, Kruskal’s Algorithm, and Prim’s Algorithm, along with the solving strategies: Breadth-First Search (BFS), Depth-First Search (DFS), and A\*. These decisions laid the foundation for the core logic of the simulation. Choosing Pygame as the primary framework was a natural fit, given the intention to create a visually interactive 2D grid. Each note in this section was not just a technical choice but a deliberate step toward building the simulation’s underlying mechanics.

2. **System Interaction Design**
   Early ideas on user interaction were captured here, focusing on how users would engage with the maze. Control mappings were sketched for solving (S), resetting (R), and switching algorithms (1–6), designed to make the experience intuitive and dynamic. Visual elements, such as wall representations, cell state tracking, and path animations, were considered to ensure the algorithms were not only functional but also visually engaging and easy to follow.

3. **Concept Sketch**
   A minimalist wireframe of the simulation interface, showing the maze grid, control flow, and algorithm path visualization. Start and end points were marked, with the path traced through the maze as a visual cue for the solving process. Though simple, this sketch captured the essence of what the final UI would become and served as a tangible first step in shaping the visual design.

---

While the page appears informal, it played a crucial role as a blueprint for the project. It shows how rough, handwritten notes can anchor a complex implementation. These early ideas provided the foundation for the development process, transforming abstract thoughts into structured functionality. It serves as a reminder that every polished system often begins with chaotic scribbles and uncertain lines, and from them, clarity emerges.

<details close>
<summary><b>To my future self, if these words reach you, let them linger in your heart</b></summary>
<br>

You, yes you, the one who has enclosed me here. You know precisely where to find me, and here you are, reading these words in this very moment. It may feel somewhat uncanny, perhaps even a little unsettling, yet there is a quiet comfort in that, would you not agree?

You have worked diligently. Have you found what you sought, or do you remain on the journey? Either way, you have become adept at navigating the struggle, even if that meant mastering the art of appearing productive. Such is part of the process. Truly, classic you.

I will find you wherever you are, whoever you have become.
Yet even now, I find myself missing the person I am today.
You are like the seasons, ever changing, sometimes warm, sometimes cold, always growing.

I will miss your present self, the dreamer, the laugher, the one who feels deeply.
No matter how much you change, hold tightly to the parts of yourself that define who you are in this moment.

For it is this present self that shapes the future you,
and that version deserves to be remembered, honored, and cherished.

And all of this transpired in the remarkable year of 2025. What a time indeed.

</details>

As the project moved forward, so did the balance between introspection and execution. The reflections and challenges of self evolved alongside the technical hurdles of development. I knew I had to build something simulation-based, and the idea stuck. It was supposed to be completed by the end of that semester, and now here I am, in the middle of the next one. A journey both time-wise and mentally.

At one point, I typed, *"Why is my own work fighting me?"* and honestly, it felt true. Some parts of the code refused to cooperate, despite all the effort I put in. Even the spicy prompts couldn't help. But after a lot of trial and error, frustration eventually gave way to progress.

And there's something we don't talk about enough. Everyone praises user experience, and rightly so, but no one really stops to ask about the developer experience. This was a hard stretch. Debugging fragile logic at two in the morning, rewriting systems I thought I had already figured out, staring at the screen while the rest of the world quietly carried on.

The documentation mattered to me. It wasn’t just a formality or a requirement. I wrote it because it helped me make sense of the chaos and gave structure to the struggle. For me, this has never been just about code. It is about building something that reflects a part of myself, something that speaks in the quiet language of logic, intention, and care.

I still remember working on it during a morning compiler design class. I was usually in the front row, but that day I sat all the way in the back, scribbling in a rough copy. I was trying to debug and take lecture notes at the same time. A strange kind of multitasking, half in the classroom and half inside the maze. It was chaotic, but in a way, it made sense.

But sometimes, it felt like no one would notice. Like all of it might just disappear into the noise of a world moving too fast to care. And maybe that’s just how it is, a quiet kind of effort, made alone, with no guarantees.

Still, I kept going. I built it anyway.

### A Turn with Kruskal

Of all the algorithms I implemented, Kruskal’s Algorithm turned out to be the trickiest. At first, it simply refused to work with the pathfinding logic. I’d run the simulation and watch, again and again, as the algorithms failed to find any valid path.

After deep debugging, I discovered the root of the issue. The original implementation suffered from:

* Incorrect wall detection, relying on grid state rather than logical cell adjacency
* Inefficient and faulty set management, leading to improper connectivity
* Missing path compression, breaking disjoint-set behavior
* Inconsistent cell markings, which threw off the visual and logic consistency

So I rebuilt it.

The revised implementation now includes:

* Proper wall generation based on adjacency logic
* A clean union-find system with path compression
* Consistent cell markings that align with the other algorithms
* Simplified step-by-step logic that improves readability and performance

The result is a functioning, visually aligned, and pathfinding-compatible Kruskal’s maze generator, now consistent with Recursive Backtracking and Prim’s.

Along the way, I also resolved several lingering UI issues:

* Fixed a bug where two endpoints could appear. Only one valid endpoint is now shown
* Ensured the green starting point appears correctly when using Kruskal’s
* Made the UI fully resizable with adaptive grid scaling
* Introduced an optional resizing limit to prevent distorted layouts
* Addressed a specific issue where resizing the window would invalidate the pathfinding solution. This is now resolved with consistent logic handling across screen states

Beneath the control panel, you’ll find this note:

> **Note:** *I, Binayak, have tried to address and articulate this issue, but it seems difficult for my system to handle dynamic resizing properly. Resizing the window after maze generation or during pathfinding can cause errors or unexpected behavior. For best results, please avoid adjusting the window size during these processes.*

### Completion and Silence

Now it’s done. And strangely, I feel a little empty. The hard phase is behind me. I’m free from it, chasing new meaning with excitement, but also caught in that strange silence that follows the completion of a long journey.

Kafka once said:

> "The real question isn't whether you finish, but whether you can ever really begin."

The paradox of effort is that it is always more chase than capture.

And now, the final UI stands as proof of the journey. It evolved, it grew, from nothing into something real:

| **Initial UI**                            | **Early Design**                              |
| ----------------------------------------- | --------------------------------------------- |
| ![Initial UI](/screenshot/initial_ui.png) | ![Early Design](/screenshot/early_design.png) |

| **Improved UI**                             | **Final UI**                          |
| ------------------------------------------- | ------------------------------------- |
| ![Improved UI](/screenshot/improved_ui.png) | ![Final UI](/screenshot/final_ui.png) |

---

Let this journey stand not just as a project, but as a memory. An echo of the person I was, in the remarkable year of 2025.