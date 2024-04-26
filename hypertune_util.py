import generated.hypertune as ht



class HypertuneWrapper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """To ensure that only one instance of the class is created, and subsequent attempts to create new instances return the existing instance."""
        if not cls._instance:
            # If no instance exists, create one
            cls._instance = super(HypertuneWrapper, cls).__new__(cls)
            # cls._instance._ht_node = ht_wrapper.initialize_hypertune({})  # Initialize the object here
        return cls._instance

    def __init__(self) -> None:
        self._ht_node = None
        # create_static_hypertune()
        self.initialize_hypertune()

    def _check_initialized(self):
        if not self._ht_node:
            raise RuntimeError("Hypertune is not initialized. Call initialize_hypertune first.")

    def initialize_hypertune(self):
        if not self._ht_node:
            environment = 'staging'
            print("environment while initializing hypertune", environment)
            self._ht_node = ht.initialize_hypertune({}).root(
                {
                    "context": {
                        "user": {
                            "id": "",
                            "email": "",
                            "name": "",
                        },
                        "environment": environment,
                    },
                }
            )
        return self._ht_node

    def get_event_details(self, command_type, **kwargs):
        """Returns priority order, response type in order of priority and ephemeral flag for the given command type."""
        self._check_initialized()
        ht_node = self._ht_node
        if ht_node is None:
            raise RuntimeError("Hypertune is not initialized. Call initialize_hypertune first.")

        priority_order = response_types_in_priority = list()
        print("getting event details for command type", command_type)

        event_obj = {
            # help command
            "help": ht_node.events().help(),
            # hello command
            "hello_new_user": ht_node.events().helloNewUser(),
            "hello_new_user_new_channel": ht_node.events().helloNewUserNewChannel(),
            "hello_existing_user": ht_node.events().helloExistingUser(),
            "hello_existing_user_new_channel": ht_node.events().helloExistingUserNewChannel(),
            # user creation/retreival
            "user_created": ht_node.events().userCreated(),
            "user_verified_fetched": ht_node.events().userVerifiedFetched(),
            "user_unverified_fetched": ht_node.events().userUnverifiedFetched(),
            "error_user_creation": ht_node.events().errorUserCreation(),
            "error_user_not_found": ht_node.events().errorUserNotFound(),
            # stream submission
            "submission_followup": ht_node.events().submissionFollowup(),
            "stream_submit_acknowledgement": ht_node.events().streamSubmitAcknowledgement(),
            "error_invalid_url": ht_node.events().errorInvalidUrl(),
            "error_invalid_source": ht_node.events().errorInvalidSource(),
            "error_video_user_not_found": ht_node.events().errorVideoUserNotFound(),
            "error_submission_streamer_not_found": ht_node.events().errorSubmissionStreamerNotFound(),
            "error_submission_stream_not_found": ht_node.events().errorSubmissionStreamNotFound(),
            # link streaming accounts
            "linking_url_processing": ht_node.events().linkingUrlProcessing(),
            "linking_url_generated": ht_node.events().linkingUrlGenerated(),
            "twitch_already_linked": ht_node.events().twitchAlreadyLinked(),
            "error_fetch_twitch_link_url": ht_node.events().errorFetchTwitchLinkUrl(),
            "error_expired_twitch_link_url": ht_node.events().errorExpiredTwitchLinkUrl(),
            # channels and guilds
            "channel_creation_success": ht_node.events().channelCreationSuccess(),
            "channel_creation_failed": ht_node.events().channelCreationFailed(),
            "error_no_channel_permission": ht_node.events().errorNoChannelPermission(),
            "error_fetch_guild": ht_node.events().errorFetchGuild(),
            # other errors
            "error_process_command": ht_node.events().errorProcessCommand(),
            "error_no_role_permission": ht_node.events().errorNoRolePermission(),
            # events
            "on_guild_join": ht_node.events().onGuildJoin(),
            # tournament
            "tournament_joining_success": ht_node.events().tournamentJoiningSuccess(),
            "tournament_joining_failed": ht_node.events().tournamentJoiningFailed(),
            "processing_tournament_joining": ht_node.events().processingTournamentJoining(),
            "tournament_headline": ht_node.events().tournamentHeadline(),
        }

        if command_type not in event_obj:
            print(f"Failed to fetch event from hypertune for command: {command_type}")
            command_type = "error_process_command"
        event = event_obj.get(command_type)

        if event is None:
            print(f"Failed to fetch event from hypertune for command: {command_type}")
        else:
            priority_order = [str(p.get(fallback="")) for p in event.priority()]

            message_type = {"DM": event.dmResponse(), "NO_DM": event.noDmResponse()}

            response_types_in_priority = [
                str(message_type.get(priority_order[i]).responseType().get(fallback=""))
                if priority_order[i] in message_type
                and message_type.get(priority_order[i]) is not None
                else None
                for i in range(len(priority_order))
            ]
        return priority_order, response_types_in_priority, event

    def get_text_or_embed_response(self, response_type, response_node):

        response_node = response_node.noDmResponse()

        if response_node is None:
            return {}, {}
        if response_type == "TEXT":
            response_detail = {"message": response_node.textResponse().get(fallback="")}
        elif response_type == "EMBED":
            response_detail = {
                "title": response_node.embedResponse().title().get(fallback=""),
                "description": response_node.embedResponse().description().get(fallback=""),
                "thumbnail": response_node.embedResponse().thumbnail().get(fallback=""),
                "footer": response_node.embedResponse().footer().get(fallback=""),
                "image": response_node.embedResponse().image().get(fallback=""),
            }

            fields = list()
            for field in response_node.embedResponse().fields():
                title = field.title().get(fallback="")
                title = "\t" if title == "blank" else title
                value = field.value().get(fallback="")
                value = "\t" if value == "blank" else value
                inline = field.inline().get(fallback=False)
                fields.append({"title": title, "value": value, "inline": inline})

            response_detail["fields"] = fields
        return response_type, response_detail


ht_wrapper = HypertuneWrapper()
