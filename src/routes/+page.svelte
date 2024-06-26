<script>
	import { source } from 'sveltekit-sse';
	import sdk from '@crossmarkio/sdk';
    import { MetaTags } from 'svelte-meta-tags';

	let walletType = sdk?.session?.address ? 'crossmark' : null;
	let address = sdk?.session?.address;
	let messages = [];
	let recordMode = false;
	let userMessage = '';
	let assistantLoader = true;
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

<div class="flex-1 p:2 sm:p-6 justify-between flex flex-col h-screen">
	<div class="flex sm:items-center justify-between py-3 border-b-2 border-gray-200">
		<div class="relative flex items-center space-x-4">
			<div class="relative">
				<img src="/android-chrome-512x512.png" alt="" class="w-14 h-14 border-2" />
			</div>
			<div class="flex flex-col leading-tight">
				<div class="text-2xl mt-1 flex items-center">
					<span class="text-gray-700 mr-3">FlowAim</span>
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
					class="inline-flex items-center justify-center rounded-lg px-4 py-3 transition duration-500 ease-in-out text-white bg-blue-500 hover:bg-blue-400 focus:outline-none"
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

<style>
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
</style>
