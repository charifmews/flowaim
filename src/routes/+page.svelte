<script>
	// import { source } from 'sveltekit-sse';
	// const value = source('/api').select('message');
    import sdk from '@crossmarkio/sdk';
    let value;
    async function signIn() {
        let { request, response, createdAt, resolvedAt } = await sdk.methods.signInAndWait();
        console.log(response.data.address);
        value = response.data.address;
        console.log("value: ", value)
    }
 
// log address
</script>

<h1>Home</h1>
{#if !value}
<button on:click={signIn}>
    Login
</button>
{/if}
{value}