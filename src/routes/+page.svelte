<script>
	import { source } from 'sveltekit-sse';
	import sdk from '@crossmarkio/sdk';

	let walletType = sdk?.session?.address ? 'crossmark' : null;
	let address = sdk?.session?.address;
	let messages = [];

	let userMessage = '';
	let connection = source('/api', {
		options: {
			headers: {
				Message: "Hello, can you help me"
			}
		}
	});
	let channel = connection.select('message');
	let transformed = channel.transform(function run(data) {
		const messageData = data.split('⸞');
		if (messageData.length === 4) {
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

	async function addMessage(message) {
		if (message.type === 'user') {
            console.log(message);
            console.log("connection restarting");
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
					addMessage({ type: 'assistant', value: messageData[2] });
					connection.close();
				}

				return `transformed: ${data}`;
			});
		}
		messages = [...messages, message];
	}
</script>

<div class="flex-1 p:2 sm:p-6 justify-between flex flex-col h-screen">
	<div class="flex sm:items-center justify-between py-3 border-b-2 border-gray-200">
		<div class="relative flex items-center space-x-4">
			<div class="relative">
				<span class="absolute text-green-500 right-0 bottom-0">
					<svg width="20" height="20">
						<circle cx="8" cy="8" r="8" fill="currentColor"></circle>
					</svg>
				</span>
				<img
					src="https://images.unsplash.com/photo-1528797890300-0787fd964724?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144"
					alt=""
					class="w-10 sm:w-16 h-10 sm:h-16 rounded-full"
				/>
			</div>
			<div class="flex flex-col leading-tight">
				<div class="text-2xl mt-1 flex items-center">
					<span class="text-gray-700 mr-3">FlowAim</span>
				</div>
				<span class="text-lg text-gray-600">Your blockchain mentor</span>
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
							src="https://images.unsplash.com/photo-1528797890300-0787fd964724?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144"
							alt=""
							class="w-10 sm:w-16 h-10 sm:h-16 rounded-full"
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
						<img
							src="https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=facearea&amp;facepad=3&amp;w=144&amp;h=144"
							alt="My profile"
							class="w-6 h-6 rounded-full order-2"
						/>
					</div>
				</div>
			{/if}
		{/each}
	</div>
	<div class="border-t-2 border-gray-200 px-4 pt-4 mb-2 sm:mb-0">
		<div class="relative flex">
			<span class="absolute inset-y-0 flex items-center">
				<button
					type="button"
					class="inline-flex items-center justify-center rounded-full h-12 w-12 transition duration-500 ease-in-out text-gray-500 hover:bg-gray-300 focus:outline-none"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						class="h-6 w-6 text-gray-600"
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
