from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
import os

def run_oryx(commands, input_video="input.mp4", output_video="output.mp4"):
    print("🚀 ORYX Engine Starting...")

    if not os.path.exists(input_video):
        print(f"❌ Input file not found: {input_video}")
        return

    try:
        clip = VideoFileClip(input_video)
    except Exception as e:
        print(f"❌ Failed to load input video: {e}")
        return

    overlays = []
    audio_clips = []
    to_delete = []
    merged_clips = []

    for cmd in commands:
        cmd_type = cmd.get("type")

        # TEXT
        if cmd_type == "txt":
            try:
                txt = TextClip(
                    txt=cmd.get("string", "BlackORYX"),
                    fontsize=int(cmd.get("txtscl", 60)) * 40,
                    color=cmd.get("clr", "white")
                )
                txt = txt.set_position(cmd.get("area", "center"))
                txt = txt.set_start(cmd.get("frm", 0)).set_end(cmd.get("to", 5))
                overlays.append(txt)
                print("✅ Added TEXT overlay")
            except Exception as e:
                print(f"⚠️ Text Error: {e}")

        # AUDIO
        elif cmd_type == "aud":
            try:
                audio_path = cmd.get("file")
                if audio_path and os.path.exists(audio_path):
                    aud = AudioFileClip(audio_path).subclip(cmd.get("frm", 0), cmd.get("to", 5))
                    audio_clips.append(aud)
                    print("✅ Added AUDIO")
                else:
                    print("⚠️ Audio file not found.")
            except Exception as e:
                print(f"⚠️ Audio Error: {e}")

        # TRANSITIONS (placeholder for fadein/fadeout etc.)
        elif cmd_type == "trsn":
            print("⚠️ Transition detected. (Not implemented yet)")

        # EFFECTS (e.g. greyscale)
        elif cmd_type == "eft":
            effect = cmd.get("effect", "greyscale")
            if effect == "greyscale":
                clip = clip.fx(vfx.blackwhite)
                print("✅ Applied GREYSCALE effect")

        # DELETE
        elif cmd_type == "del":
            file_to_delete = cmd.get("target")
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
                print(f"✅ Deleted: {file_to_delete}")
            else:
                print(f"⚠️ File to delete not found: {file_to_delete}")

        # MERGE (support later by user input merge(x,y))
        elif cmd_type == "merge":
            print("⚠️ Merge command detected. (Manual implementation coming)")

        elif cmd_type == "run":
            continue  # just skip, not a media block

        else:
            print(f"⚠️ Unknown block type: {cmd_type}")

    # Add overlays
    try:
        final = CompositeVideoClip([clip] + overlays)

        # Set audio if any
        if audio_clips:
            print("🔊 Merging audio clips...")
            final_audio = audio_clips[0]
            for ac in audio_clips[1:]:
                final_audio = final_audio.set_audio(ac)
            final = final.set_audio(final_audio)

        print("🎬 Rendering final video...")
        final.write_videofile(output_video, codec="libx264", fps=24)
        print("✅ ORYX Compilation Complete.")
    except Exception as e:
        print(f"❌ Final render failed: {e}")
