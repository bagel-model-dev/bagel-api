        """Minimal BAGEL example: create one prediction and print the output URL(s)."""
        import bagel_api

        output = bagel_api.run({
    "prompt": "Make this a 90s cartoon",
    "input_image": "https://example.com/input.png"
})
        print(output)
