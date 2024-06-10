<script>
    import { source } from 'sveltekit-sse';
    import sdk from '@crossmarkio/sdk';
    import { MetaTags } from 'svelte-meta-tags';
    import { writable } from 'svelte/store';
    import { onMount } from 'svelte';

    let walletType = sdk?.session?.address ? 'crossmark' : null;
    let address = sdk?.session?.address;
    let messages = [];
    let recordMode = false;
    let userMessage = '';
    let assistantLoader = true;
    let ammpoolData = writable([]);
    let selectedAccount = null;
    
    let connection = source('/api', {
        options: {
            headers: {
                Message: 'Greet me and ask me what I want to do'
            }
        }
    });
    let channel = connection.select('message');
    let transformed = channel.transform(function run(data) {
        const messageData = data.split('⸞');
        if (messageData.length === 4) {
            assistantLoader = false;
            addMessage({ type: 'assistant', value: messageData[2] });
            connection.close();
        }

        return `transformed: ${data}`;
    });

    $: console.log({ $transformed });

    const recentAccounts = writable([]);
    
    async function loadAMMPoolData() {
        try {
            const response = await fetch('/full_ammpool_data.json');
            if (!response.ok) {
                throw new Error('Failed to fetch AMM Pool data');
            }
            const data = await response.json();
            ammpoolData.set(data);
        } catch (error) {
            console.error('Error loading AMM Pool data:', error);
        }
    }

    async function signIn() {
        let { request, response, createdAt, resolvedAt } = await sdk.methods.signInAndWait();
        walletType = 'crossmark';
        address = response.data.address;
    }

    async function signOut() {
        walletType = null;
        address = null;
    }

    function sendPayment(address, amount) {
        crossMarkSendPayment(address, amount);
    }

    function sendBridgePayment(address, amount) {
        crossMarkSendBridgePayment(address, amount);
    }

    async function crossMarkSendPayment(destinationAddress, amount) {
        await sdk.methods.signAndSubmitAndWait({
            TransactionType: 'Payment',
            Account: address,
            Destination: destinationAddress,
            Amount: `${amount}000000`
        });
    }

    async function crossMarkSendBridgePayment(destinationAddress, amount) {
        const destAddress = destinationAddress.startsWith('0x')
            ? destinationAddress.slice(2)
            : destinationAddress;
        await sdk.methods.signAndSubmitAndWait({
            TransactionType: 'Payment',
            Account: address,
            Destination: 'rfEf91bLxrTVC76vw1W3Ur8Jk4Lwujskmb', // Axelar's XRPL multisig account
            Amount: `${amount}000000`,
            Memos: [
                {
                    Memo: {
                        MemoData: destAddress, // your ETH recipient address, without the 0x prefix
                        MemoType: '64657374696E6174696F6E5F61646472657373' // hex("destination_address")
                    }
                },
                {
                    Memo: {
                        MemoData: '657468657265756D', // hex("ethereum")
                        MemoType: '64657374696E6174696F6E5F636861696E' // hex("destination_chain")
                    }
                },
                {
                    Memo: {
                        MemoData: '0000000000000000000000000000000000000000000000000000000000000000', // bytes32(0) indicates pure token transfer, without GMP
                        MemoType: '7061796C6F61645F68617368' // hex("payload_hash")
                    }
                }
            ]
        });
    }

    async function addMessage(message) {
        if (message.type === 'user') {
            assistantLoader = true;
            connection = source('/api', {
                options: {
                    headers: {
                        Message: userMessage
                    }
                }
            });
            channel = connection.select('message');
            transformed = channel.transform(function run(data) {
                const messageData = data.split('⸞');
                if (messageData.length === 4) {
                    const action = messageData[0].replace(/[^a-zA-Z_]/g, '');
                    switch (action) {
                        case 'SEND_MONEY':
                            const send_input = JSON.parse(messageData[1]);
                            sendPayment(send_input.address, send_input.amount);
                            break;

                        case 'BRIDGE':
                            const bridge_input = JSON.parse(messageData[1]);
                            sendBridgePayment(bridge_input.address, bridge_input.amount);
                            break;

                        default:
                            console.error('unmatched');
                            break;
                    }
                    assistantLoader = false;
                    addMessage({ type: 'assistant', value: messageData[2] });
                    connection.close();
                }

                return `transformed: ${data}`;
            });
        }
        messages = [...messages, message];
    }

    function startRecording() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Your browser does not support speech recognition. Please use Google Chrome.');
        } else {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false; // Stop automatically after one recognition
            recognition.interimResults = false; // No interim results
            recognition.lang = 'en-US'; // Language
            recognition.start();

            recognition.onstart = function () {
                recordMode = true;
            };

            recognition.onend = function () {
                recordMode = false;
            };

            recognition.onresult = function (event) {
                console.log('works');
                const transcript = event.results[0][0].transcript;
                userMessage = transcript;
            };

            recognition.onerror = function (event) {
                console.error(event);
            };
        }
    }

    onMount(() => {
        loadAMMPoolData();
    });

    function selectAccount(account) {
		if (account) {
			selectedAccount = account;
			const message = `Asset pair: ${account["Asset Pair"]} with AMM account: ${account["AMM Account"]}`;
			
			// Insert the message at the cursor position
			const inputField = document.querySelector('#message-input');
			const cursorPosition = inputField.selectionStart;
			
			userMessage = userMessage.slice(0, cursorPosition) + message + userMessage.slice(cursorPosition);

			// Set the new cursor position after the inserted message
			setTimeout(() => {
				inputField.setSelectionRange(cursorPosition + message.length, cursorPosition + message.length);
				inputField.focus();
			}, 0);

			recentAccounts.update((recent) => {
				const updated = [account, ...recent.filter(acc => acc["AMM Account"] !== account["AMM Account"])];
				return updated.slice(0, 3);
			});
		} else {
			console.error('Account data is undefined');
		}
	}




    function updateRecentAccounts(account) {
        const existingIndex = recentAccounts.findIndex(a => a["AMM Account"] === account["AMM Account"]);
        if (existingIndex !== -1) {
            recentAccounts.splice(existingIndex, 1);
        }
        recentAccounts.unshift(account);
        if (recentAccounts.length > 3) {
            recentAccounts.pop();
        }
        localStorage.setItem('recentAccounts', JSON.stringify(recentAccounts));
        selectAccount(account);
    }
</script>

<MetaTags
    title="Your personal XRP AI guide"
    titleTemplate="%s | FlowAim"
    description="We help crypto beginners onboard XRP, advice and create transactions. No more struggle, just the fastest flow."
    canonical="https://flowaim.com/"
    openGraph={{
        url: 'https://flowaim.com/',
        title: 'Open Graph Title',
        description: 'Open Graph Description',
        images: [
            {
                url: 'https://flowaim.com/social-media-whippet.webp',
                alt: 'Your personal XRP AI guide | FlowAim'
            }
        ],
        siteName: 'FlowAim'
    }}
/>

<div class="flex h-screen">
    <!-- Sidebar -->
    <div class="sidebar w-64 bg-gray-100 p-4 border-r-2 border-gray-200 flex-shrink-0">
		<div class="bg-gray-800 px-2 py-1 flex items-center justify-center">
			<h2 class="text-xl font-bold text-white" style="font-family: 'Nunito', sans-serif;">Accounts</h2>
		</div>
		
        <div class="amm-accounts h-1/2 overflow-y-auto mb-4">
            <div>
                <!-- <h3 class="text-lg font-medium mb-2">Recent</h3> -->
                {#each $recentAccounts as account}
                    <button
                        class="p-2 mb-2 bg-white rounded shadow cursor-pointer hover:bg-gray-200"
                        on:click={() => selectAccount(account)}
						
					>	{account["Rank"]}.
						{account["Asset Pair"]}
						<span class="text-sm text-gray-500 font-bold">
							{account["AMM Account"].substring(0, 4)}
						</span>
                    </button>
                {/each}
            </div>
            <div>
                <h3 class="text-lg font-medium mb-2 text-gray-500">-Recent-</h3>
                {#each $ammpoolData as account (account["AMM Account"])}
                    <button
                        class="p-2 mb-2 bg-white rounded shadow cursor-pointer hover:bg-gray-200"
                        on:click={() => selectAccount(account)}
                    >
					{account["Rank"]}.
					{account["Asset Pair"]}
					<span class="text-sm text-gray-500 font-bold">
						{account["AMM Account"].substring(0, 4)}
					</span>
                    </button>
                {/each}
            </div>
        </div>

        <h2 class="text-xl font-semibold mb-4">DEX</h2>
        <div class="dex-accounts h-1/2 overflow-y-auto">
            <!-- DEX Accounts content goes here -->
        </div>
    </div>

    <!-- Chat area -->
    <div class="flex-1 p-2 sm:p-6 flex flex-col">
        <div class="flex sm:items-center justify-between py-3 border-b-2 border-gray-200">
            <div class="relative flex items-center space-x-4">
                <div class="relative">
                    <img src="/android-chrome-512x512.png" alt="" class="w-14 h-14 border-2" />
                </div>
				<div class="flex flex-col leading-tight">
					<div class="text-2xl mt-1 flex items-center flowaim-container">
						<span class="text-gray-700"><span class="font-normal">Flow</span><b>Aim</b></span>
					  </div>
					
					
                    <span class="text-lg text-gray-600">Your XRP guide</span>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button
                    type="button"
                    class="inline-flex items-center justify-center rounded-lg border h-10 w-10 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-6 w-6"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        ></path>
                    </svg>
                </button>
                <button
                    type="button"
                    class="inline-flex items-center justify-center rounded-lg border h-10 w-10 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-6 w-6"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                        ></path>
                    </svg>
                </button>
                {#if !address}
                    <button
                        on:click={signIn}
                        class="px-2 inline-flex items-center justify-center rounded-lg border h-10 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none"
                    >
                        <img class="h-6 mr-2" src="crossmark.webp" alt="" />
                        Login
                    </button>
                {:else}
                    <button
                        on:click={signOut}
                        class="px-2 items-center justify-center rounded-lg border h-10 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none ml-4 flex"
                    >
                        <img class="h-6 mr-2" src="crossmark.webp" alt="" />
                        <p>Sign out {address.substr(0, 3)}...{address.substr(-3)}</p>
                    </button>
                {/if}
            </div>
        </div>

        <div
            id="messages"
            class="flex flex-col h-full space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch"
        >
            {#each messages as message}
                {#if message.type === 'assistant'}
                    <div class="chat-message">
                        <div class="flex items-end">
                            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
                                <div>
                                    <span
                                        class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600"
                                        >{message.value}</span
                                    >
                                </div>
                            </div>
                            <img
                                src="/android-chrome-192x192.png"
                                alt=""
                                class="w-14 h-14 rounded-full border-4 border-gray-200"
                            />
                        </div>
                    </div>
                {:else}
                    <div class="chat-message">
                        <div class="flex items-end justify-end">
                            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-1 items-end">
                                <div>
                                    <span
                                        class="px-4 py-2 rounded-lg inline-block rounded-br-none bg-blue-600 text-white"
                                        >{message.value}</span
                                    >
                                </div>
                            </div>
                            <img src="/husky-logo.png" alt="My profile" class="w-14 h-14 rounded-full order-2" />
                        </div>
                    </div>
                {/if}
            {/each}
            {#if assistantLoader}
                <div class="chat-message">
                    <div class="flex items-end">
                        <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
                            <div>
                                <span
                                    class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600 relative"
                                >
                                    Typing...
                                    <span
                                        class="animate-ping absolute top-0 right-0 inline-flex w-2 h-2 rounded-full bg-orange-500 opacity-75"
                                    ></span>
                                </span>
                            </div>
                        </div>
                        <img
                            src="/android-chrome-192x192.png"
                            alt=""
                            class="w-14 h-14 rounded-full border-4 border-gray-200"
                        />
                    </div>
                </div>
            {/if}
        </div>
        <div class="border-t-2 border-gray-200 px-4 pt-4 mb-2 sm:mb-0">
			<div class="relative flex">
				<span class="absolute inset-y-0 flex items-center">
					<button
						on:click={startRecording}
						type="button"
						class="inline-flex items-center justify-center rounded-full h-12 w-12 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							class={`h-6 w-6 ${recordMode ? 'text-red-600' : 'text-gray-600'}`}
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
							></path>
						</svg>
					</button>
				</span>
				<input
					type="text"
					id="message-input"
					placeholder="Write your message!"
					bind:value={userMessage}
					on:keydown={(e) => {
						if (e.key === 'Enter') {
							addMessage({ type: 'user', value: userMessage });
							userMessage = '';
						}
					}}
					class="w-full focus:outline-none focus:placeholder-gray-400 text-gray-600 placeholder-gray-600 pl-12 bg-gray-200 rounded-md py-3"
				/>
				<div class="absolute right-0 items-center inset-y-0 hidden sm:flex">
					<button
						on:click={() => {
							addMessage({ type: 'user', value: userMessage });
							userMessage = '';
						}}
						type="button"
						class="send-button"
					>
						<span class="font-bold">Send</span>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							class="h-6 w-6 ml-2 transform rotate-90"
						>
							<path
								d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"
							></path>
						</svg>
					</button>
				</div>
			</div>
		</div>		
    </div>
</div>


<style>
	 @font-face {
		font-family: 'Nunito';
		src: url('/fonts/Nunito-Regular.ttf') format('truetype');
		font-weight: 400; 
	}

	@font-face {
		font-family: 'Nunito';
		src: url('/fonts/Nunito-Bold.ttf') format('truetype');
		font-weight: 700;
	}

	.flowaim-container {
		font-family: 'Nunito', sans-serif;
	}
    .scrollbar-w-2::-webkit-scrollbar {
        width: 0.25rem;
        height: 0.25rem;
    }

    .scrollbar-track-blue-lighter::-webkit-scrollbar-track {
        --bg-opacity: 1;
        background-color: #f7fafc;
        background-color: rgba(247, 250, 252, var(--bg-opacity));
    }

    .scrollbar-thumb-blue::-webkit-scrollbar-thumb {
        --bg-opacity: 1;
        background-color: #edf2f7;
        background-color: rgba(237, 242, 247, var(--bg-opacity));
    }

    .scrollbar-thumb-rounded::-webkit-scrollbar-thumb {
        border-radius: 0.25rem;
    }

    .sidebar {
        width: 16rem; /* 64px */
        background-color: #f7fafc; /* bg-gray-100 */
        padding: 1rem; /* p-4 */
        border-right: 2px solid #e5e7eb; /* border-r-2 border-gray-200 */
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
    }

    .amm-accounts, .dex-accounts {
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #edf2f7 #f7fafc;
    }

    .amm-accounts::-webkit-scrollbar, .dex-accounts::-webkit-scrollbar {
        width: 0.25rem;
        height: 0.25rem;
    }

    .amm-accounts::-webkit-scrollbar-track, .dex-accounts::-webkit-scrollbar-track {
        background-color: #f7fafc; /* bg-gray-100 */
    }

    .amm-accounts::-webkit-scrollbar-thumb, .dex-accounts::-webkit-scrollbar-thumb {
        background-color: #edf2f7; /* scrollbar-thumb */
        border-radius: 0.25rem;
    }

    button {
        display: block;
        width: 100%;
        text-align: left;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #fff; /* bg-white */
        border: none;
        border-radius: 0.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); /* shadow */
        cursor: pointer;
        transition: background-color 0.2s ease-in-out;
    }

    button:hover {
        background-color: #e2e8f0; /* hover:bg-gray-200 */
    }

    .send-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 0.25rem;
        padding: 0.75rem 1rem;
        transition: background-color 0.5s ease-in-out;
        color: #fff;
        background-color: #3b82f6; /* bg-blue-500 */
    }

    .send-button:hover {
        background-color: #2563eb; /* bg-blue-400 */
    }

    .send-button:focus {
        outline: none;
    }
</style>
