# Flowaim

FlowAim is your personal XRP AI guide. We help crypto beginners onboard, advice and create transactions. No more struggle, just the fastest flow. Let me show you how we achieve that

## Overview
This project is a Svelte application that leverages the OpenAI API to create an assistant capable of interpreting user prompts and generating commands for the Crossmarks wallet. We have a the AIM framework which stands for 

* Action (Which function we need to initiate)
* Input (JSON)
* Message (Which we show in the UI)

This prevents using OpenAI function calling which needs to calls to OpenAI and is not the best suited for chat applications. For Web3 the AIM flow is especially suitable because of the heavy
front-end logic.

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

2. Access the application in your browser at `http://localhost:5173/`.

## Transactions that were AI triggered

You can try yourself on https://flowaim.com on Ripple Testnet! 

Or check these transactions: 

send 1 XRP: [EBE060A6E23C0B6F406A754409FE4688F37BA2DDFD7FB57D8D02302EB7032475](https://testnet.xrpl.org/transactions/EBE060A6E23C0B6F406A754409FE4688F37BA2DDFD7FB57D8D02302EB7032475/simple)
send 1 XRP to Ethereum Sepolia with Axelar: [C91A53730284F069B01EF036331008E7D39D3254AED468785EBE47D02D4FA702](https://testnet.xrpl.org/transactions/C91A53730284F069B01EF036331008E7D39D3254AED468785EBE47D02D4FA702/simple)

## AMM Scraper
The project includes a data scraper located in the `amm_scraper` directory. This scraper fetches data from `https://xrpscan.com/amms` and processes it into JSON format. For detailed instructions on using the scraper, refer to the [AMM Scraper README](./amm_scraper/README.md).


<!-- Interacting with apps/blockchains should be conversational.
It should flow naturally, and your money/assets should always aim
to earn the most interest, dividends, or capital gains,
depending on your personal risk profile. -->
