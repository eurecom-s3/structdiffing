/* console.h v5.16.0 */
struct consw {
	struct module *owner;
	const char *(*con_startup)(void);
	void	(*con_init)(struct vc_data *vc, int init);
	void	(*con_deinit)(struct vc_data *vc);
	void	(*con_clear)(struct vc_data *vc, int sy, int sx, int height,
			int width);
	void	(*con_putc)(struct vc_data *vc, int c, int ypos, int xpos);
	void	(*con_putcs)(struct vc_data *vc, const unsigned short *s,
			int count, int ypos, int xpos);
	void	(*con_cursor)(struct vc_data *vc, int mode);
	bool	(*con_scroll)(struct vc_data *vc, unsigned int top,
			unsigned int bottom, enum con_scroll dir,
			unsigned int lines);
	int	(*con_switch)(struct vc_data *vc);
	int	(*con_blank)(struct vc_data *vc, int blank, int mode_switch);
	int	(*con_font_set)(struct vc_data *vc, struct console_font *font,
			unsigned int flags);
	int	(*con_font_get)(struct vc_data *vc, struct console_font *font);
	int	(*con_font_default)(struct vc_data *vc,
			struct console_font *font, char *name);
	int     (*con_resize)(struct vc_data *vc, unsigned int width,
			unsigned int height, unsigned int user);
	void	(*con_set_palette)(struct vc_data *vc,
			const unsigned char *table);
	void	(*con_scrolldelta)(struct vc_data *vc, int lines);
	int	(*con_set_origin)(struct vc_data *vc);
	void	(*con_save_screen)(struct vc_data *vc);
	u8	(*con_build_attr)(struct vc_data *vc, u8 color,
			enum vc_intensity intensity,
			bool blink, bool underline, bool reverse, bool italic);
	void	(*con_invert_region)(struct vc_data *vc, u16 *p, int count);
	u16    *(*con_screen_pos)(const struct vc_data *vc, int offset);
	unsigned long (*con_getxy)(struct vc_data *vc, unsigned long position,
			int *px, int *py);
	/*
	 * Flush the video console driver's scrollback buffer
	 */
	void	(*con_flush_scrollback)(struct vc_data *vc);
	/*
	 * Prepare the console for the debugger.  This includes, but is not
	 * limited to, unblanking the console, loading an appropriate
	 * palette, and allowing debugger generated output.
	 */
	int	(*con_debug_enter)(struct vc_data *vc);
	/*
	 * Restore the console to its pre-debug state as closely as possible.
	 */
	int	(*con_debug_leave)(struct vc_data *vc);
};