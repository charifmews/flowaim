<script>
	import { source } from 'sveltekit-sse';
	const value = source('/api').select('message');
</script>

{$value}
