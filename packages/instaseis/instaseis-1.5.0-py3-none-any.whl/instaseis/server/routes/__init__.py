import asyncio


# Custom event loop policy to replace deprecated AnyThreadEventLoopPolicy
# This allows event loops to be created in any thread, which is needed
# for Tornado's ThreadPoolExecutor usage
class _AnyThreadEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Custom event loop policy that allows loops in any thread."""

    def get_event_loop(self):
        try:
            return super().get_event_loop()
        except RuntimeError:
            # If no event loop exists in this thread, create one
            loop = self.new_event_loop()
            self.set_event_loop(loop)
            return loop


# Set the custom policy
asyncio.set_event_loop_policy(_AnyThreadEventLoopPolicy())
