# Flowaim

## Overview
This project is a Svelte application that leverages the OpenAI API to create an assistant capable of interpreting user prompts and generating commands for Crossmarks.io. The assistant processes user requests and returns structured JSON responses with specific actions and inputs.

### Introduction
Imagine interacting with apps and blockchains as naturally as having a conversation. Let your assets work smarter, effortlessly maximizing returns—whether it's interest, dividends, or capital gains—all perfectly aligned with your personal risk profile.

## Prerequisites
- Node.js
- SvelteKit
- OpenAI API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/charifmews/flowaim.git
    ```

2. Navigate to the project directory:
    ```bash
    cd flowaim
    ```

3. Install dependencies:
    ```bash
    npm install
    ```

4. Set up environment variables:
    - Create a `.env` file in the project root.
    - Add your OpenAI API key:
      ```plaintext
      PRIVATE_OPENAI_API_KEY=your_openai_api_key
      ```

## Usage

1. Run the Svelte application:
    ```bash
    npm run dev
    ```

2. Access the application in your browser at `http://localhost:3000`.

## AMM Scraper
The project includes a data scraper located in the `amm_scraper` directory. This scraper fetches data from `https://xrpscan.com/amms` and processes it into JSON format. For detailed instructions on using the scraper, refer to the [AMM Scraper README](./amm_scraper/README.md).


<!-- Interacting with apps/blockchains should be conversational.
It should flow naturally, and your money/assets should always aim
to earn the most interest, dividends, or capital gains,
depending on your personal risk profile. -->
