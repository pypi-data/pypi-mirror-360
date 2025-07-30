# PSEUDOCODE: Response Formatter Utility
#
# FUNCTION FormatOutput(prompt, claude_response, sdk_messages)
# BEGIN
#     PRINT "USER: " + prompt
#     PRINT "CLAUDE: " + claude_response
#     FOR each message IN sdk_messages DO
#         PRINT "SDK: " + CleanMessage(message)
#     ENDFOR
# END
#
# FUNCTION CleanMessage(message)
# BEGIN
#     IF message contains "session_id" THEN
#         RETURN "Session started"
#     ELSIF message contains "duration_ms" THEN
#         RETURN "Completed in " + duration + "ms"
#     ELSIF message contains "tool_result" THEN
#         RETURN "Tool executed"
#     ELSE
#         RETURN "System message"
#     ENDIF
# END

class ResponseFormatter:
    def format_output(self, prompt, claude_response, sdk_messages):
        print(f"USER: {prompt}")
        print(f"CLAUDE: {claude_response}")
        for message in sdk_messages:
            print(f"SDK: {self.clean_message(message)}")
    
    def clean_message(self, message):
        message_str = str(message)
        if "session_id" in message_str:
            return "Session started"
        elif "duration_ms" in message_str:
            # Extract duration if possible
            try:
                start = message_str.find("duration_ms=") + 12
                end = message_str.find(",", start)
                if end == -1:
                    end = message_str.find(")", start)
                duration = message_str[start:end]
                return f"Completed in {duration}ms"
            except:
                return "Completed"
        elif "tool_result" in message_str:
            return "Tool executed"
        else:
            return "System message"