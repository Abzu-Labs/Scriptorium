<script lang="ts">
	import { Auth } from '@supabase/auth-ui-svelte';
	import { supabaseClient } from '../db';
	import { ThemeSupa, type SocialLayout, type ViewType } from '@supabase/auth-ui-shared';
	import MenuIcon from './MenuIcon.svelte';
	import ToggleButton from './ToggleButton.svelte';

	const classes: { [key: string]: string } = {
		'rgb(202, 37, 37)': 'container-redshadow',
		'rgb(65, 163, 35)': 'container-greenshadow',
		'rgb(8, 107, 177)': 'container-blueshadow',
		'rgb(235, 115, 29)': 'container-orangeshadow'
	};

	const colors = [
		'rgb(202, 37, 37)',
		'rgb(65, 163, 35)',
		'rgb(8, 107, 177)',
		'rgb(235, 115, 29)'
	] as const;

	const socialAlignments = ['horizontal', 'vertical'] as const;

	const radii = ['5px', '10px', '20px'] as const;

	const views: { id: ViewType; title: string }[] = [
		{ id: 'sign_in', title: 'Sign In' },
		{ id: 'sign_up', title: 'Sign Up' },
		{ id: 'magic_link', title: 'Magic Link' },
		{ id: 'forgotten_password', title: 'Forgotten Password' },
		{ id: 'update_password', title: 'Update Password' },
		{ id: 'verify_otp', title: 'Verify Otp' }
	];

	let brandColor = colors[0];
	let socialLayout = socialAlignments[1] satisfies SocialLayout;
	let borderRadius = radii[0];
	let view = views[0];
</script>

<svelte:head>
	<title>Auth UI Svelte</title>
</svelte:head>

<div class="dark:bg-scale-200 bg-scale-100 relative py-2 pb-16">
	<div
		class="sm:py-18 gap container relative mx-auto grid grid-cols-12 px-6 py-16 md:gap-16 md:py-24 lg:gap-16 lg:px-16 lg:py-24 xl:px-20"
	>
		<div class="relative col-span-12 mb-16 md:col-span-7 md:mb-0 lg:col-span-6">
			<div class="relative lg:mx-auto lg:max-w-md bg-zinc-900">
				<div class={classes[brandColor]}>
					<div class="border-scale-400 bg-scale-300 relative rounded-xl px-8 py-12 drop-shadow-sm">
						<div class="mb-6 flex flex-col gap-6">
							<div class="flex items-center gap-3">
								<h1 class="text-scale-1200 text-2xl">Scriptorium</h1>
							</div>
							<p class="text-scale-1100 text-auth-widget-test">Sign in today for Supa stuff</p>
						</div>
						<Auth
							{supabaseClient}
							theme="dark"
							view={view.id}
							appearance={{
								theme: ThemeSupa,
								style: {
									button: `border-radius: ${borderRadius}; border-color: rgba(0,0,0,0);`
								},
								variables: {
									default: {
										colors: {
											brand: brandColor,
											brandAccent: `gray`
										},
										radii: {
											borderRadiusButton: borderRadius,
											buttonBorderRadius: borderRadius,
											inputBorderRadius: borderRadius
										}
									}
								}
							}}
							providers={['apple', 'google', 'github']}
							{socialLayout}
						/>
					</div>
				</div>
			</div>
		</div>

	</div>
</div>

<style>
	.container-redshadow {
		min-width: 364px;
		box-shadow: -2px 1px 69px 5px rgb(54, 54, 54);
		border-radius: 1rem;
	}

	.container-greenshadow {
		min-width: 364px;
		box-shadow: -2px 1px 69px 5px rgb(65, 163, 35);
		border-radius: 1rem;
	}

	.container-blueshadow {
		min-width: 364px;
		box-shadow: -2px 1px 69px 5px rgb(8, 107, 177);
		border-radius: 1rem;
	}

	.container-orangeshadow {
		min-width: 364px;
		box-shadow: -2px 1px 69px 5px rgb(235, 115, 29);
		border-radius: 1rem;
	}
</style>
