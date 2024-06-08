import OpenAI from 'openai';
import { PRIVATE_OPENAI_API_KEY } from '$env/static/private';
import { produce } from 'sveltekit-sse';

const openai = new OpenAI({ apiKey: PRIVATE_OPENAI_API_KEY });

/** @type {import('./$types').RequestHandler} */
export function POST() {
	return produce(async function start({ emit }) {
		const assistant = await openai.beta.assistants.retrieve('asst_AbauCA98lAw8e8moeWkjjj0m');

		const thread = await openai.beta.threads.create();

		const message1 = await openai.beta.threads.messages.create(thread.id, {
			role: 'assistant',
			content: `You only reply in the following format:
              "ACTION⸞INPUT⸞MESSAGE"
              
              The ACTIONS are: 
              ["SEND_MONEY", "BALANCE"]
  
              The INPUT depends on the money the user wants to transfer. 
              You will return valid JSON with the amount, address
            `
		});

		const message2 = await openai.beta.threads.messages.create(thread.id, {
			role: 'user',
			content: 'I want to transfer money to 0x1234567890abcdef and the amount is 1000'
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
