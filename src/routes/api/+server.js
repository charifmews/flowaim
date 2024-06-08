import OpenAI from 'openai';
import { PRIVATE_OPENAI_API_KEY } from '$env/static/private';
import { produce } from 'sveltekit-sse';

const openai = new OpenAI({ apiKey: PRIVATE_OPENAI_API_KEY });

/** @type {import('./$types').RequestHandler} */
export async function POST({ request }) {
	return produce(async function start({ emit }) {
		const assistant = await openai.beta.assistants.retrieve('asst_AbauCA98lAw8e8moeWkjjj0m');

		const thread = await openai.beta.threads.create();

		await openai.beta.threads.messages.create(thread.id, {
			role: 'assistant',
			content: `You only reply in the following format:
              "ACTION⸞INPUT⸞MESSAGE⸞END"
              
              The ACTIONS are: 
              ["SEND_MONEY", "BALANCE", "BRIDGE", "CONVERSATE"]

              The INPUT depends on the money the user wants to transfer. 

              For action BALANCE you will return an empty JSON
              For action SEND_MONEY you will return valid JSON with the amount, address
              For action BRIDGE you will return valid JSON with the amount, address

              Message is always friendly and informative.

              You always end with '⸞END'
            `
		});

		await openai.beta.threads.messages.create(thread.id, {
			role: 'user',
			content: request.headers.get('message')
		});

		const run = openai.beta.threads.runs
			.stream(thread.id, {
				assistant_id: assistant.id
			})
			.on('textDelta', (textDelta, snapshot) => {
				// console.log('textDelta', textDelta.value)
				emit('message', snapshot.value);
			});
	});
}
