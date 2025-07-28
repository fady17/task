Prepared by: Fady 
Date: 28 july 2025
Subject: Scaling our Real-Time Services for Multi-Party Communication and AI Integration

1. The Problem: The Architectural Limits of a Simple WebRTC Backend

Our project's goal is to create a robust, real-time collaboration platform featuring both an AI assistant and multi-user communication. We successfully implemented a one-to-one AI chat using a WebRTC data channel and built a proof-of-concept for real-time voice using a simple "echo" server.

However, as we moved to implement our next critical feature—a multi-party conference room for human-to-human calls—we encountered a significant architectural challenge that is common in real-time application development.

What We Built: A Custom Selective Forwarding Unit (SFU)

To support multi-party calls, we evolved our simple echo server into a lightweight Selective Forwarding Unit (SFU).

Architecture: Each participant connects directly to our custom voice-api service. When a user speaks, the server receives their audio stream and is responsible for forwarding (or "relaying") that stream to every other participant in the room.

Successes: We successfully proved this model works for two participants. Our voice-api, built with Python and aiortc, was able to correctly manage the state of a room and route audio packets between two peers. This validated our entire networking stack, including the TURN server for NAT traversal.

The Emerging Challenge: While functional for 2-3 users, we identified a major bottleneck. As the number of participants grows, the complexity of managing the connections and media streams on the server increases exponentially. Specifically, our custom SFU would need to handle:

Complex Renegotiation: Every time a user joins or leaves a call, every other participant's connection must be "renegotiated" to add or remove the audio track. Our attempts to implement this revealed significant race conditions and state management issues that led to dropped calls for the initial participants.

Scalability Concerns: Our simple Python application, while effective, is not optimized for the high-throughput, low-latency packet routing required to support dozens of concurrent audio streams.

Cross-Browser Compatibility: We discovered inconsistencies in how different browsers (Chrome vs. Safari) handle WebRTC negotiation, which would require us to write and maintain complex, browser-specific logic on both the client and server.

Feature Creep: To make it production-grade, our small voice-api would need to be expanded with features like network quality monitoring, adaptive bitrate control, and server-side recording—essentially, we would have to build a full-featured media server from scratch.

Conclusion of Our Findings: We successfully built a working SFU prototype, which was an invaluable learning experience. However, this process revealed that building, scaling, and maintaining a production-grade WebRTC media server is a massive engineering undertaking in itself. It was diverting focus from our project's core goal: building the AI pipeline and the application's unique features.

2. The Solution: Adopting an Open-Source, Production-Grade Media Server

Based on the challenges identified with our custom SFU, we conducted research into industry-standard solutions for managing WebRTC at scale. This led us to discover LiveKit, an open-source WebRTC infrastructure project that is specifically designed to solve the exact problems we were encountering.

By integrating LiveKit, we can offload the complex media server logic to a specialized, battle-tested component and refocus our own development efforts on building our unique application features.

The New Proposed Architecture:

The new architecture is cleaner, more scalable, and accelerates our development roadmap.

LiveKit Server (The New Media Backbone):

We will add the official livekit/livekit-server as a new service in our Docker stack.

This single component will replace our entire custom voice-api service. It is a powerful, pre-built SFU that handles all media routing, scalability, and cross-browser compatibility out of the box.

Our Main api Service (The Application Controller):

Our role shifts from managing media packets to managing access and logic.

We will add the LiveKit Server SDK to our FastAPI backend.

We will create a new, simple endpoint (e.g., /api/livekit/token) whose only job is to generate secure access tokens for clients who want to join a room. This keeps our application in control of who can access what.

Frontend (The Smart Client):

We will replace our custom useConferenceCall hook with the official livekit-client and @livekit/components-react libraries.

These libraries handle 100% of the complex WebRTC logic on the client side. The frontend's only responsibilities are to (1) fetch a token from our api service and (2) render the pre-built, high-quality React components for the video/audio conference.

Pipecat Integration (The AI Participant):

The path to our AI pipeline becomes incredibly elegant. The Pipecat agent will use the LiveKit Python SDK to join a conference call just like a human client.

It will request a token from our api service.

It will receive audio from all participants via the LiveKitSource.

It will send its synthesized speech back to the room via the LiveKitSink.

LiveKit handles all the complex audio mixing and distribution automatically.

Benefits of this Architectural Pivot:

Accelerated Development: We are no longer spending time debugging low-level networking and race conditions. We can immediately start building the high-value features: the user interface and the AI pipeline.

Massive Scalability: LiveKit is designed to scale to thousands of concurrent users, a level of performance our custom solution could never achieve without significant investment.

Production-Ready Features: We get features like network quality statistics, server-side recording capabilities, and robust error handling for free.

Alignment with Industry Standards: By building on a popular open-source platform, we ensure our application is maintainable and can benefit from the ongoing improvements made by the LiveKit community.

This strategic shift allows us to stand on the shoulders of giants, leveraging a powerful open-source media server to handle the heavy lifting of real-time communication, so we can focus on what makes our application unique and valuable.